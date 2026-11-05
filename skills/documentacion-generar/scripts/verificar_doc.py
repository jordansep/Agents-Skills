#!/usr/bin/env python3
"""Verifica documentación Markdown contra un prompt de estilo de documentacion-estilo.

Uso:
    python3 verificar_doc.py --prompt docs/prompt-estilo.md docs/manual/
    python3 verificar_doc.py --prompt docs/prompt-estilo.md docs/manual/01-intro.md docs/manual/02-uso.md
    python3 verificar_doc.py --prompt docs/prompt-estilo.md docs/entrega/    # entrega: multiarchivo

Revisa estructura, numeración de títulos, tablas, figuras, avisos, siglas,
números, largo de oraciones y que el prólogo no esté redactado. Si el prompt declara tablas estadísticas
(`tablas:`), también revisa las reglas de APA 7 (cero inicial, separador
decimal y nota de los asteriscos). Con `entrega: multiarchivo` recibe una carpeta con
un índice y un archivo por punto (DEC-008): numera por archivo (DEC-009) y revisa
los enlaces del índice y el control de versiones (DEC-010). Termina con código 1 si
encuentra errores, y con código 2 si el prompt o las rutas no sirven.
Solo usa la biblioteca estándar.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

SIN_NUMERAR_BASE = {
    "control de versiones", "portada", "resumen", "abstract", "agradecimientos",
    "dedicatoria", "indice", "indice general", "indice de figuras", "indice de tablas",
    "lista de siglas y abreviaturas", "siglas y abreviaturas", "glosario",
    "referencias", "bibliografia", "anexos", "apendices",
    "prefacio", "prologo", "epigrafe", "indice alfabetico", "colofon",
}
MARCADOR_PROLOGO = "[PENDIENTE: texto del prologuista]"
SIGLAS_BASE = {"URL", "PDF", "HTML", "CSS", "HTTP", "HTTPS", "JSON", "XML", "USB", "ID", "OK", "SI", "PNG", "SVG", "SQL"}
METODOS_HTTP = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
SIGLAS_BASE |= METODOS_HTTP
AVISOS = {"nota", "consejo", "advertencia", "peligro"}
# Ejes de clasificación del prompt (references/escritura.md, §4 bis). Son opcionales: los prompts
# viejos solo traen `audiencia`, que se acepta sin aviso.
EJES = {
    "proposito": {"expositivo", "analitico", "argumentativo", "instructivo", "narrativo", "mixto"},
    "ambito": {"cientifico", "tecnico", "academico", "institucional", "profesional"},
    "lector": {"experto", "especialista", "publico_general", "mixto"},
}
ROMANOS = re.compile(r"^[IVXLC]+$")
CONTEXTO_NUMERO = re.compile(r"(secci[oó]n|apartado|cap[ií]tulo|versi[oó]n|figura|tabla|v)\s*$", re.I)


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.strip().lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto)


def valor_yaml(crudo):
    """Quita las comillas de un escalar; las comillas dobles admiten escapes (\\", \\n...)."""
    crudo = crudo.strip()
    if len(crudo) >= 2 and crudo[0] == crudo[-1] == '"':
        try:
            return json.loads(crudo)
        except ValueError:
            return crudo[1:-1]
    if len(crudo) >= 2 and crudo[0] == crudo[-1] == "'":
        return crudo[1:-1].replace("''", "'")
    return crudo


def leer_frontmatter(texto):
    """Lee un encabezado YAML simple (claves, valores y listas). Devuelve (datos, resto, líneas_saltadas)."""
    if not texto.startswith("---"):
        return {}, texto, 0
    lineas = texto.split("\n")
    fin = next((i for i in range(1, len(lineas)) if lineas[i].strip() == "---"), None)
    if fin is None:
        return {}, texto, 0
    datos, clave = {}, None
    for linea in lineas[1:fin]:
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s+(.*)$", linea)
        if item and clave:
            if not isinstance(datos.get(clave), list):
                datos[clave] = []
            datos[clave].append(valor_yaml(item.group(1)))
            continue
        par = re.match(r"^([\w\-]+):\s*(.*)$", linea)
        if par:
            clave, valor = par.group(1), valor_yaml(par.group(2))
            datos[clave] = valor if valor else []
    return datos, "\n".join(lineas[fin + 1:]), fin + 1


class Informe:
    def __init__(self):
        self.errores, self.advertencias, self.info = [], [], []

    def error(self, donde, msg):
        self.errores.append(f"{donde}: {msg}")

    def aviso(self, donde, msg):
        self.advertencias.append(f"{donde}: {msg}")


# Plantillas cuyas leyendas siguen APA 7 (references/plantillas/ de documentacion-estilo).
PLANTILLAS_APA7 = ("trabajo-campo-unc",)


def bloques(archivos):
    """Devuelve las líneas de todos los archivos con su ubicación, marcando las que están en código."""
    salida = []
    for ruta in archivos:
        texto = ruta.read_text(encoding="utf-8")
        _, cuerpo, saltadas = leer_frontmatter(texto)
        en_codigo, lenguaje = False, ""
        for n, linea in enumerate(cuerpo.split("\n"), start=saltadas + 1):
            valla = re.match(r"^\s*(```|~~~)\s*([\w\-]*)", linea)
            if valla:
                if not en_codigo:
                    en_codigo, lenguaje = True, valla.group(2).lower()
                    salida.append((f"{ruta}:{n}", linea, "inicio_codigo", lenguaje))
                else:
                    en_codigo = False
                    salida.append((f"{ruta}:{n}", linea, "fin_codigo", lenguaje))
                continue
            salida.append((f"{ruta}:{n}", linea, "codigo" if en_codigo else "texto", lenguaje if en_codigo else ""))
    return salida


def siguiente_no_vacia(lineas, i, paso):
    j = i + paso
    while 0 <= j < len(lineas) and not lineas[j][1].strip():
        j += paso
    return lineas[j] if 0 <= j < len(lineas) else None


def estilo_leyendas(prompt):
    """«apa7» si el prompt lo pide en `leyendas` o declara una plantilla que usa APA 7; si no, «clasica»."""
    explicito = normalizar(str(prompt.get("leyendas", "")))
    if explicito in {"apa7", "apa 7", "apa"}:
        return "apa7"
    if explicito:
        return "clasica"
    plantilla = normalizar(str(prompt.get("plantilla", "")))
    return "apa7" if any(p in plantilla for p in PLANTILLAS_APA7) else "clasica"


# Número de una leyenda o de una cita: entero («Tabla 4») o con prefijo («Tabla 4.1», DEC-009).
NUMERO_ELEMENTO = r"\d+(?:\.\d+)*"


def numero_elemento(texto):
    """«04.1» se compara como «4.1»."""
    return ".".join(str(int(p)) for p in texto.split("."))


def leyenda_clasica(linea, clase):
    """«**Tabla N.** Título» en una sola línea, con N entero o con prefijo. Devuelve N como texto, o None."""
    m = re.match(rf"^\*{{0,2}}{clase} ({NUMERO_ELEMENTO})\.(?!\d)", linea[1].strip()) if linea else None
    return numero_elemento(m.group(1)) if m else None


def leyenda_apa(lineas, i, clase):
    """APA 7: «**Tabla N**» y en la línea siguiente «*Título*», justo antes del elemento i. Devuelve N como texto, o None."""
    j = i - 1
    while j >= 0 and not lineas[j][1].strip():
        j -= 1
    if j < 0 or not re.match(r"^(\*|_)[^*_].*(\*|_)$", lineas[j][1].strip()):
        return None
    numero = siguiente_no_vacia(lineas, j, -1)
    m = re.match(rf"^\*\*{clase} ({NUMERO_ELEMENTO})\*\*$", numero[1].strip()) if numero else None
    return numero_elemento(m.group(1)) if m else None


# Tipos de tabla del configurador que siguen las reglas estadísticas de APA 7 (ESTADISTICAS en configurador.html).
TABLAS_ESTADISTICAS = {
    "frecuencia", "contingencia", "correlacion", "regresion", "anova",
    "demografica", "descriptivos", "fiabilidad", "pruebas",
}
# Símbolos de valores que no pueden superar 1 y van sin cero inicial: p, r, β, α, ω, η², η²p.
SIMBOLO_SIN_CERO = r"(?:p|r|β|α|ω|η(?:²|2)p?)"
VALOR_EN_TEXTO = re.compile(rf"(?<![\w])\*{{0,2}}({SIMBOLO_SIN_CERO})\*{{0,2}}\s*([=<>≤≥])\s*(0?)([.,])(\d+)")
CABECERA_SIN_CERO = re.compile(rf"^{SIMBOLO_SIN_CERO}$")
CELDA_DECIMAL = re.compile(r"^(?:<\s*)?[−-]?(0?)([.,])\d+(?:\\?\*)*$")
CON_ASTERISCOS = re.compile(r"\d(?:\\?\*){1,3}$")


def usa_tablas_estadisticas(prompt):
    return bool({normalizar(str(t)) for t in prompt.get("tablas", []) or []} & TABLAS_ESTADISTICAS)


def celdas(linea):
    return [c.strip() for c in re.split(r"(?<!\\)\|", linea.strip().strip("|"))]


def tablas_markdown(lineas):
    """Tablas del documento: [(dónde empieza, cabecera normalizada, [(dónde, celdas)])]."""
    salida, i = [], 0
    while i < len(lineas):
        _, linea, tipo, _ = lineas[i]
        sig = lineas[i + 1][1] if i + 1 < len(lineas) else ""
        if tipo == "texto" and linea.lstrip().startswith("|") and re.match(r"^\s*\|?\s*:?-{3,}", sig):
            cabecera = [normalizar(re.sub(r"[*_`\\]", "", c)) for c in celdas(linea)]
            j, filas = i + 2, []
            while j < len(lineas) and lineas[j][2] == "texto" and lineas[j][1].lstrip().startswith("|"):
                filas.append((lineas[j][0], celdas(lineas[j][1])))
                j += 1
            salida.append((lineas[i][0], cabecera, filas))
            i = j
        else:
            i += 1
    return salida


def columna(cabecera, *nombres):
    """Índice de la primera columna cuyo encabezado empieza con alguno de los nombres, o None."""
    return next((k for k, c in enumerate(cabecera) if any(c.startswith(n) for n in nombres)), None)


NIVELES_RIESGO = ((1, 4, "bajo"), (5, 9, "medio"), (10, 16, "alto"), (20, 25, "critico"))


def verificar_tecnicas(lineas, tipos, inf):
    """Tablas técnicas: métodos HTTP, nivel de riesgo = probabilidad × impacto y casos de prueba en la trazabilidad."""
    for donde, cab, filas in tablas_markdown(lineas):
        metodo = columna(cab, "metodo")
        if "endpoints" in tipos and metodo is not None:
            for d, fila in filas:
                valor = re.sub(r"[`*]", "", fila[metodo]).strip() if metodo < len(fila) else ""
                if valor and valor not in METODOS_HTTP:
                    inf.aviso(d, f"método «{valor}»: se esperaba GET, POST, PUT, PATCH o DELETE, en mayúsculas")

        prob, imp, nivel = columna(cab, "probabilidad"), columna(cab, "impacto"), columna(cab, "nivel")
        if "riesgos" in tipos and None not in (prob, imp, nivel):
            anteriores = []
            for d, fila in filas:
                try:
                    p, i = int(fila[prob]), int(fila[imp])
                    m = re.match(r"^(\d+)\s*(?:\((\w+)\))?", fila[nivel])
                except (IndexError, ValueError):
                    continue
                if not m:
                    continue
                n = int(m.group(1))
                if n != p * i:
                    inf.aviso(d, f"nivel de riesgo {n}: con probabilidad {p} e impacto {i} debería ser {p * i}")
                categoria = next((c for a, b, c in NIVELES_RIESGO if a <= n <= b), None)
                if m.group(2) and categoria and normalizar(m.group(2)) != categoria:
                    inf.aviso(d, f"nivel {n} es «{categoria.replace('critico', 'crítico')}», no «{m.group(2)}»")
                anteriores.append(n)
            if anteriores != sorted(anteriores, reverse=True):
                inf.aviso(donde, "los riesgos no están ordenados de mayor a menor nivel")

        caso = columna(cab, "caso de prueba")
        if "trazabilidad" in tipos and caso is not None:
            for d, fila in filas:
                valor = fila[caso].strip() if caso < len(fila) else ""
                if valor in {"", "—", "-", "–"}:
                    inf.aviso(d, f"el requisito «{fila[0]}» no tiene caso de prueba (si falta, «[PENDIENTE: caso de prueba]»)")


def verificar_estadistica(lineas, decimal_coma, inf):
    """APA 7 en tablas estadísticas: sin cero inicial en p, r, β, α, ω y η²; separador decimal; nota de los asteriscos."""
    malo = "." if decimal_coma else ","
    nombre = "coma" if decimal_coma else "punto"

    def revisar_valor(donde, texto, simbolo, cero, sep):
        if cero:
            inf.aviso(donde, f"«{texto}»: {simbolo} va sin cero inicial (APA 7)")
        if sep == malo:
            inf.aviso(donde, f"«{texto}»: el separador decimal del prompt es la {nombre}")

    for donde, linea, tipo, _ in lineas:
        if tipo == "texto":
            for m in VALOR_EN_TEXTO.finditer(re.sub(r"`[^`]*`", "", linea)):
                revisar_valor(donde, m.group(0).replace("*", ""), m.group(1), m.group(3), m.group(4))

    i = 0
    while i < len(lineas):
        donde, linea, tipo, _ = lineas[i]
        sig = lineas[i + 1][1] if i + 1 < len(lineas) else ""
        if not (tipo == "texto" and linea.lstrip().startswith("|") and re.match(r"^\s*\|?\s*:?-{3,}", sig)):
            i += 1
            continue
        cabecera = [re.sub(r"[*_\\]", "", c) for c in celdas(linea)]
        sin_cero = {k for k, c in enumerate(cabecera) if CABECERA_SIN_CERO.match(c)}
        j, asteriscos = i + 2, False
        while j < len(lineas) and lineas[j][2] == "texto" and lineas[j][1].lstrip().startswith("|"):
            for k, celda in enumerate(celdas(lineas[j][1])):
                asteriscos = asteriscos or bool(CON_ASTERISCOS.search(celda))
                m = CELDA_DECIMAL.match(celda)
                if m and k in sin_cero:
                    revisar_valor(lineas[j][0], celda, cabecera[k], m.group(1), m.group(2))
            j += 1
        if asteriscos:
            despues = [l for _, l, t, _ in lineas[j:j + 6] if t == "texto" and l.strip()][:3]
            if not any(re.search(r"\bp\s*<", re.sub(r"[*_\\]", "", l)) for l in despues):
                s = "," if decimal_coma else "."
                inf.aviso(donde, f"la tabla marca significación con asteriscos pero no tiene la nota debajo («*p < {s}05. **p < {s}01.»)")
        i = j


ROTULO_AVISO = re.compile(r"^>\s*\*\*([^*]+?)[.:]\*\*")
COMILLAS = re.compile(r"“([^”]+)”|«([^»]+)»|\"([^\"\n]+)\"")


def bloques_de_cita(lineas):
    """Bloques de «>» que no son avisos: [(dónde empieza, texto)]."""
    salida, actual = [], None
    for donde, linea, tipo, _ in lineas:
        es_cita = tipo == "texto" and linea.lstrip().startswith(">")
        if es_cita and actual is None and not ROTULO_AVISO.match(linea.lstrip()):
            actual = [donde, []]
            salida.append(actual)
        if not es_cita:
            actual = None
        elif actual is not None:
            actual[1].append(re.sub(r"^\s*>\s?", "", linea))
    return [(d, " ".join(t)) for d, t in salida]


def verificar_academicos(lineas, componentes, numeros, inf):
    """Notas al pie siempre; citas en bloque, hipótesis, palabras clave, anexos e índices según `componentes`."""
    texto = [(d, l) for d, l, t, _ in lineas if t == "texto"]

    # Notas al pie: cada llamada [^n] tiene su definición y cada definición, su llamada.
    definiciones = {m.group(1): d for d, l in texto for m in [re.match(r"^\[\^([^\]]+)\]:", l)] if m}
    llamadas = {}
    for d, l in texto:
        for m in re.finditer(r"\[\^([^\]]+)\](?!:)", re.sub(r"`[^`]*`", "", l)):
            llamadas.setdefault(m.group(1), d)
    for n, d in llamadas.items():
        if n not in definiciones:
            inf.error(d, f"la nota al pie [^{n}] no tiene definición")
    for n, d in definiciones.items():
        if n not in llamadas:
            inf.aviso(d, f"la nota al pie [^{n}] está definida pero no se usa en el texto")

    if "cita_bloque" in componentes:
        for d, cita in bloques_de_cita(lineas):
            palabras = len(re.findall(r"\w+", re.sub(r"\([^)]*\)\s*$", "", cita)))
            if palabras < 40:
                inf.aviso(d, f"cita en bloque de {palabras} palabras: las de menos de 40 van en el texto, entre comillas")
        for d, l in texto:
            if l.lstrip().startswith(">"):
                continue
            for m in COMILLAS.finditer(l):
                palabras = len(re.findall(r"\w+", next(g for g in m.groups() if g)))
                if palabras >= 40:
                    inf.aviso(d, f"cita de {palabras} palabras entre comillas: las de 40 o más van en bloque")

    if "hipotesis" in componentes:
        esperado = 1
        for d, l in texto:
            m = re.match(r"^\s*\*\*H(\d+)\.\*\*", l)
            if m and m.group(1) != "0":
                if int(m.group(1)) != esperado:
                    inf.error(d, f"hipótesis H{m.group(1)}: la numeración no es continua; se esperaba H{esperado}")
                esperado = int(m.group(1)) + 1

    if "palabras_clave" in componentes:
        claves = [(d, l) for d, l in texto if re.match(r"^\s*\*\*Palabras clave:?\*\*:?", l, re.I)]
        if not claves:
            inf.aviso("resumen", "falta la línea «**Palabras clave:**» debajo del resumen")
        for d, l in claves:
            resto = re.sub(r"^\s*\*\*Palabras clave:?\*\*:?\s*", "", l, flags=re.I).strip().rstrip(".")
            terminos = [t for t in resto.split(";") if t.strip()]
            if ";" not in resto and "," in resto:
                inf.aviso(d, "las palabras clave se separan con punto y coma")
            elif not 3 <= len(terminos) <= 5:
                inf.aviso(d, f"{len(terminos)} palabras clave; deben ser de 3 a 5")

    if "anexos" in componentes:
        anexos = [(d, m.group(1)) for d, l in texto for m in [re.match(r"^#{1,3}\s+Anexo ([A-Z])\b", l)] if m]
        for k, (d, letra) in enumerate(anexos):
            esperada = chr(ord("A") + k)
            if letra != esperada:
                inf.error(d, f"Anexo {letra}: las letras no siguen el orden; se esperaba Anexo {esperada}")
        cuerpo = "\n".join(l for _, l in texto if not re.match(r"^#", l))
        for d, letra in anexos:
            if not re.search(rf"\bAnexo {letra}\b", cuerpo):
                inf.aviso(d, f"el Anexo {letra} no se menciona en el texto")

    if "indices" in componentes:
        titulos = {normalizar(re.sub(r"^#+\s+", "", l)) for _, l in texto if re.match(r"^#{1,3}\s", l)}
        for clase, nombre in (("Tabla", "indice de tablas"), ("Figura", "indice de figuras")):
            if numeros[clase] and nombre not in titulos:
                inf.aviso("estructura", f"el documento tiene {clase.lower()}s pero no «{nombre.replace('indice', 'Índice')}»")


ID_MEMORIA = re.compile(r"\b(DEC|DP)-(\d{3})\b")


def leer_memoria(ruta):
    """Devuelve {«DEC-001»: «pendiente», ...} con las entradas de un archivo de memoria, o None si no existe."""
    if not ruta or not Path(ruta).is_file():
        return None
    entradas, actual = {}, None
    for linea in Path(ruta).read_text(encoding="utf-8").split("\n"):
        titulo = re.match(r"^##\s+((?:DEC|DP)-\d{3})\b", linea)
        if titulo:
            actual = titulo.group(1)
            entradas[actual] = ""
            continue
        estado = re.match(r"^-\s*\*\*Estado\*\*:\s*(\w+)", linea)
        if estado and actual and not entradas[actual]:
            entradas[actual] = normalizar(estado.group(1))
    return entradas


def verificar_referencias(lineas, numeros, inf):
    """Cada «Tabla N» o «Figura N» citada en el texto tiene que existir."""
    existentes = {clase: {n for _, n in lista} for clase, lista in numeros.items()}
    for donde, linea, tipo, _ in lineas:
        if tipo != "texto":
            continue
        sin_codigo = re.sub(r"`[^`]*`", "", linea)
        for m in re.finditer(rf"(?<!\*\*)(?<!\w)(Tabla|Figura) ({NUMERO_ELEMENTO})(?![\d.]*\*\*)(?![\d\w])(?!\.\d)", sin_codigo, re.I):
            clase, n = m.group(1).capitalize(), numero_elemento(m.group(2))
            if n not in existentes[clase]:
                inf.error(donde, f"se cita la {clase} {n}, que no existe en el documento")


def verificar_memoria(lineas, memorias, inf):
    """Los DEC-NNN y DP-NNN citados existen en la memoria del agente o del proyecto."""
    nombres = {"DEC": "la memoria del agente (memoria/decisiones.md)", "DP": "la memoria del proyecto (decisiones-estilo.md)"}
    sin_archivo = set()
    for donde, linea, tipo, _ in lineas:
        if tipo != "texto":
            continue
        for m in ID_MEMORIA.finditer(linea):
            prefijo, ident = m.group(1), m.group(0)
            entradas = memorias.get(prefijo)
            if entradas is None:
                if prefijo not in sin_archivo:
                    sin_archivo.add(prefijo)
                    (inf.error if prefijo == "DP" else inf.aviso)(donde, f"se cita {ident} pero no se encontró {nombres[prefijo]}")
                continue
            if ident not in entradas:
                inf.error(donde, f"se cita {ident}, que no existe en {nombres[prefijo]}")
            elif entradas[ident] == "descartada":
                inf.aviso(donde, f"se cita {ident}, que está descartada")


def verificar_ejes(prompt, inf):
    for eje, validos in EJES.items():
        valor = prompt.get(eje)
        if valor in (None, [], ""):
            continue
        # Valor exacto: el configurador escribe identificadores en minúscula y sin tildes.
        if str(valor).strip() not in validos:
            inf.aviso("prompt", f"valor de eje desconocido: {eje}: {valor} (válidos: {', '.join(sorted(validos))})")


def verificar_prologo(lineas, inf):
    """El prólogo lo escribe otra persona: su sección solo puede tener el marcador del prologuista,
    aunque esté en cursiva o en negrita. Una sección vacía también da aviso: el marcador es obligatorio."""
    nivel_prologo, inicio, redactado, con_marcador = None, None, False, False
    for donde, linea, tipo, _ in lineas + [("", "# fin", "texto", "")]:
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", linea) if tipo == "texto" else None
        if m and (nivel_prologo is None or len(m.group(1)) <= nivel_prologo):
            if nivel_prologo is not None and redactado:
                inf.aviso(inicio, "la sección «Prólogo» tiene texto: el prólogo lo escribe otra persona; "
                                  "deja «[PENDIENTE: texto del prologuista]»")
            elif nivel_prologo is not None and not con_marcador:
                inf.aviso(inicio, "la sección «Prólogo» está vacía: deja «[PENDIENTE: texto del prologuista]»")
            nombre = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", m.group(2)).rstrip(".")
            nivel_prologo = len(m.group(1)) if normalizar(nombre) == "prologo" else None
            inicio, redactado, con_marcador = donde, False, False
            continue
        texto = linea.strip().strip("*_").strip()
        if nivel_prologo is not None and texto:
            if normalizar(texto) == normalizar(MARCADOR_PROLOGO):
                con_marcador = True
            else:
                redactado = True


# Componentes propios de las plantillas (COMPONENTES_PLANTILLA en configurador.html y references/plantillas/).
ESTADOS_PUNTO = {"completo", "parcial", "no"}
CUMPLE = {"si", "parcial", "no"}
TITULO_PUNTO = re.compile(r"^###\s+\d+ · .+ — (Completo|Parcial|No) \((\d+)\s?%\)\s*$")
FUENTE_CAPITULO = re.compile(r"^\*\*Documento fuente:\s*(\*[^*]+\*|\[PENDIENTE[^\]]*\])\.?\*\*\s*$")
RAYAS = {"", "—", "-", "–"}


def capitulos_del_documento(lineas, documento):
    """[(nombre normalizado, ubicación, líneas de texto del capítulo)] y las líneas anteriores al primer capítulo.
    El primer H1 igual al título del documento no es un capítulo."""
    texto = [(d, l) for d, l, t, _ in lineas if t == "texto"]
    caps, antes, actual, primero = [], [], None, True
    for d, l in texto:
        m = re.match(r"^#\s+(?:\d+\.?\s+)?(.*?)\s*$", l)
        if m:
            nombre = normalizar(m.group(1).rstrip("."))
            if primero and documento and nombre == documento:
                primero = False
                continue
            primero = False
            actual = (nombre, d, [])
            caps.append(actual)
        elif actual is None:
            antes.append((d, l))
        else:
            actual[2].append((d, l))
    return caps, antes


def oraciones(texto):
    texto = re.sub(r"\([^)]*\)", "", texto)
    return [o for o in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡])", texto.strip()) if re.search(r"\w", o)]


def verificar_plantilla(lineas, propios, prompt, inf):
    """Controles de los componentes propios que se pueden revisar en Markdown."""
    documento = normalizar(prompt.get("documento", ""))
    caps, antes = capitulos_del_documento(lineas, documento)
    zonas = {normalizar(str(x)) for k in ("pretextuales", "postextuales") for x in prompt.get(k, []) or []}
    textuales = [c for c in caps if c[0] not in zonas]
    preambulo = "\n".join(l for _, l in antes)
    tablas = tablas_markdown(lineas)

    if "documento_fuente" in propios:
        for nombre, d, cuerpo in textuales:
            ultima = next((l.strip() for _, l in reversed(cuerpo) if l.strip()), "")
            if not FUENTE_CAPITULO.match(ultima):
                inf.aviso(d, f"el capítulo «{nombre}» no cierra con «**Documento fuente: *nombre del documento*.**»")

    if "termino_definido" in propios:
        for d, l, t, _ in lineas:
            if t == "texto" and re.match(r"^\s*[-*+]\s+\*\*[^*:]+\*\*\s*:", l):
                inf.aviso(d, "los dos puntos del término van dentro de la negrita: «**Término:** texto»")

    for clave, campos in (("datos_documento", ("Sistema", "Documento", "Estado")), ("ficha_corrida", ("Commit", "Fecha", "Criterio")), ("familia", ("Familia",))):
        if clave in propios:
            for campo in campos:
                if not re.search(rf"\*\*{campo}:\*\*", preambulo):
                    inf.aviso("encabezado", f"falta «**{campo}:**» debajo del título, antes del primer capítulo")
    if "ficha_corrida" in propios and re.search(r"\*\*Commit:\*\*", preambulo) and not re.search(r"\*\*Commit:\*\*\s*`[^`]+`", preambulo):
        inf.aviso("encabezado", "el commit de la ficha de corrida va en código: «**Commit:** `abc1234`»")

    for donde, cab, filas in tablas:
        est, compl = columna(cab, "estado"), columna(cab, "completitud")
        if "estado_completitud" in propios and est is not None and compl is not None:
            for d, fila in filas:
                valor = normalizar(re.sub(r"[*`]", "", fila[est])) if est < len(fila) else ""
                if valor not in ESTADOS_PUNTO:
                    inf.aviso(d, f"estado «{fila[est] if est < len(fila) else ''}»: se esperaba Completo, Parcial o No")
                m = re.search(r"(\d+)\s?%", fila[compl]) if compl < len(fila) else None
                if m and (valor == "completo") != (m.group(1) == "100"):
                    inf.aviso(d, f"estado «{fila[est]}» con {m.group(1)} %: Completo es siempre 100 %")
        cumple, evid = columna(cab, "¿cumple?", "cumple"), columna(cab, "evidencia")
        if "criterio_evidencia" in propios and cumple is not None:
            for d, fila in filas:
                valor = normalizar(re.sub(r"[*`]", "", fila[cumple])) if cumple < len(fila) else ""
                if valor not in CUMPLE:
                    inf.aviso(d, f"«¿Cumple?» es «{fila[cumple] if cumple < len(fila) else ''}»: se esperaba Sí, Parcial o No")
                elif valor != "no" and evid is not None:
                    ev = fila[evid].strip() if evid < len(fila) else ""
                    if not re.search(r"\([^)]+\)", ev):
                        inf.aviso(d, "la evidencia no cita el lugar exacto entre paréntesis, como «(01:124-152)»")
        estimado = columna(cab, "tiempo estimado")
        if "agenda" in propios and estimado is not None and filas:
            d, ultima = filas[-1]
            if normalizar(re.sub(r"[*`]", "", ultima[0])) != "tiempo total":
                inf.aviso(donde, "la agenda no termina con la fila «**Tiempo total**»")
            else:
                minutos = [re.match(r"^\**\s*(\d+)\s*min", f[estimado].strip()) if estimado < len(f) else None for _, f in filas]
                if all(minutos):
                    suma, total = sum(int(m.group(1)) for m in minutos[:-1]), int(minutos[-1].group(1))
                    if suma != total:
                        inf.aviso(d, f"el tiempo total es {total} min, pero los tiempos estimados suman {suma} min")

    if "criterio_evidencia" in propios:
        texto = [(d, l) for d, l, t, _ in lineas if t == "texto"]
        puntos = [k for k, (_, l) in enumerate(texto) if re.match(r"^###\s+\d+ ·", l)]
        for n, k in enumerate(puntos):
            d, l = texto[k]
            if not TITULO_PUNTO.match(l.strip()):
                inf.aviso(d, "el título del punto debe ser «### N · Nombre — Estado (NN %)», con Completo, Parcial o No")
            fin = puntos[n + 1] if n + 1 < len(puntos) else next((j for j in range(k + 1, len(texto)) if re.match(r"^#{1,2}\s", texto[j][1])), len(texto))
            bloque = [x for _, x in texto[k + 1:fin]]
            siguiente = next((x.strip() for x in bloque if x.strip()), "")
            if not re.match(r"^Archivo:", siguiente):
                inf.aviso(d, "falta la línea «Archivo: `ruta`» debajo del título del punto")
            if not any(re.match(r"^\s*\*\*Para completar:\*\*", x) for x in bloque):
                inf.aviso(d, "el punto no tiene el párrafo «**Para completar:**»")

    if "preguntas_abiertas" in propios:
        texto = [(d, l) for d, l, t, _ in lineas if t == "texto"]
        anterior = None
        for k, (d, l) in enumerate(texto):
            m = re.match(r"^\s*\*\*(\d+)\.(\d+)\*\*\s+\S", l)
            if not m:
                continue
            bloque, numero = int(m.group(1)), int(m.group(2))
            esperado = (anterior[0], anterior[1] + 1) if anterior and anterior[0] == bloque else (bloque, 1)
            if (bloque, numero) != esperado or (anterior and bloque < anterior[0]):
                inf.aviso(d, f"pregunta {bloque}.{numero}: la numeración no es continua; se esperaba {esperado[0]}.{esperado[1]}")
            anterior = (bloque, numero)
            n = 0
            for _, x in texto[k + 1:]:
                if not x.strip():
                    continue
                if re.match(r"^\s*_{3,}\s*$", x):
                    n += 1
                    continue
                break
            if not 3 <= n <= 4:
                inf.aviso(d, f"la pregunta {bloque}.{numero} tiene {n} líneas para responder; deben ser de 3 a 4")

    def capitulo(nombre):
        return next((c for c in caps if c[0] == normalizar(nombre)), None)

    if "intencion" in propios:
        c = capitulo("Intención")
        if c:
            prosa = " ".join(l.strip().strip("*_") for _, l in c[2] if l.strip() and not re.match(r"^\s*(#|\||!\[)", l))
            if len(oraciones(prosa)) > 2:
                inf.aviso(c[1], f"la intención tiene {len(oraciones(prosa))} oraciones; debe tener una o dos")

    if "cuando_usar" in propios:
        c = capitulo("Cuándo usarlo")
        if c:
            dentro = {d for d, _ in c[2]}
            cabs = [cab for donde, cab, _ in tablas if donde in dentro]
            if not any([normalizar(x) for x in cab] == ["si usarlo", "no usarlo"] for cab in cabs):
                inf.aviso(c[1], "«Cuándo usarlo» debe ser una tabla con solo dos columnas: «Sí usarlo» y «No usarlo»")

    if "antetitulo" in propios or "una_idea" in propios:
        for nombre, d, cuerpo in textuales:
            if "una_idea" in propios and any(re.match(r"^##\s", l) for _, l in cuerpo):
                inf.aviso(d, f"la lámina «{nombre}» tiene secciones: una idea por lámina; divídela en varias")
            if "antetitulo" in propios:
                parrafos = [l.strip() for _, l in cuerpo if l.strip()]
                if not parrafos or not re.match(r"^\*\*[^*]+\*\*$", parrafos[0]):
                    inf.aviso(d, f"la lámina «{nombre}» no empieza con el antetítulo en negrita, en su propia línea")
                    continue
                bajada = []
                for _, l in cuerpo[next(i for i, (_, x) in enumerate(cuerpo) if x.strip()) + 1:]:
                    if not l.strip():
                        if bajada:
                            break
                        continue
                    if re.match(r"^\s*(#|\||!\[|[-*+]\s|>|```)", l):
                        break
                    bajada.append(l.strip())
                if len(oraciones(" ".join(bajada))) > 3:
                    inf.aviso(d, f"la bajada de «{nombre}» tiene {len(oraciones(' '.join(bajada)))} oraciones; deben ser de una a tres")


ENTREGAS = ("multiarchivo", "unico")
INDICE_POR_DEFECTO = "README.md"
PATRON_POR_DEFECTO = "NN - Nombre.md"
ENLACE = re.compile(r"(?<!!)\[[^\]]*\]\(\s*(<[^>]*>|(?:[^()\s]|\([^()\s]*\))+)[^)]*\)")


class Entrega:
    """Entrega `multiarchivo` (DEC-008): índice y puntos [(número, ruta)] en orden de lectura."""

    def __init__(self, carpeta, indice, puntos):
        self.carpeta, self.indice, self.puntos = carpeta, indice, puntos
        self.archivos = ([indice] if indice else []) + [r for _, r in puntos]
        self.numeros = {str(r): n for n, r in puntos}


def ruta_de(donde):
    """La ruta de una ubicación «ruta:línea»; la ruta puede tener «:» (C:\\docs)."""
    return donde.rsplit(":", 1)[0]


def campo_sin_comentario(prompt, clave, defecto=""):
    """Escalar del prompt sin su comentario final: la plantilla usa «valor  # opciones»."""
    valor = prompt.get(clave)
    if valor in (None, [], ""):
        return defecto
    return valor_yaml(re.sub(r"(?:^|\s+)#.*$", "", str(valor))) or defecto


def regex_patron(patron):
    """`NN` es el número, `Nombre` el texto y lo demás es literal. Un `NN` repetido debe valer lo mismo."""
    partes, con_numero = [], False
    for parte in re.split(r"(NN|Nombre)", patron):
        if parte == "NN":
            partes.append("(?P=numero)" if con_numero else r"(?P<numero>\d+)")
            con_numero = True
        else:
            partes.append(".+" if parte == "Nombre" else re.escape(parte))
    if not con_numero:
        raise ValueError(f"entrega_patron «{patron}» no tiene NN: el número del punto es obligatorio")
    return re.compile("".join(partes))


def preparar_entrega(prompt, rutas, prompt_ruta, inf):
    """Lee `entrega`, `entrega_indice` y `entrega_patron`. Con `unico` devuelve None; con `multiarchivo`,
    la Entrega en orden de lectura. Lo que impide empezar lanza ValueError (código 2); lo demás va al informe."""
    modo = campo_sin_comentario(prompt, "entrega", "unico")
    if modo not in ENTREGAS:
        raise ValueError(f"valor de entrega desconocido: {modo} (válidos: {', '.join(ENTREGAS)})")
    if modo == "unico":
        return None
    if len(rutas) != 1 or not rutas[0].is_dir():
        raise ValueError("con `entrega: multiarchivo` hay que indicar una sola carpeta")
    carpeta = rutas[0]
    indice = campo_sin_comentario(prompt, "entrega_indice", INDICE_POR_DEFECTO)
    patron = campo_sin_comentario(prompt, "entrega_patron", PATRON_POR_DEFECTO)
    if re.search(r"[/\\]", indice) or not indice.lower().endswith(".md"):
        raise ValueError(f"entrega_indice «{indice}» debe ser un nombre de archivo .md de la carpeta")
    if re.search(r"[/\\]", patron) or not patron.lower().endswith(".md"):
        raise ValueError(f"entrega_patron «{patron}» debe terminar en .md y no puede tener barras")
    regex = regex_patron(patron)

    prompt_real = prompt_ruta.resolve()
    archivos = sorted(
        f for f in carpeta.iterdir()
        if f.is_file() and f.suffix.lower() == ".md" and f.resolve() != prompt_real and f.name != "decisiones-estilo.md")
    if not archivos:
        raise ValueError(f"no se encontraron archivos .md en {carpeta}")

    ruta_indice, puntos = None, []
    for f in archivos:
        coincide = regex.fullmatch(f.name)
        if f.name == indice:
            ruta_indice = f
        elif coincide:
            puntos.append((int(coincide.group("numero")), f))
        else:
            inf.error(str(f), f"el archivo no cumple el patrón «{patron}» ni es el índice")
    if ruta_indice is None:
        inf.error(str(carpeta), f"falta el índice «{indice}»")
    puntos.sort(key=lambda p: (p[0], p[1].name))

    vistos = set()
    for n, f in puntos:
        if n in vistos:
            inf.error(str(f), f"número {n} repetido en la entrega")
        vistos.add(n)
    if puntos:
        for n in range(min(1, puntos[0][0]), puntos[-1][0]):
            if n not in vistos:
                inf.aviso(str(carpeta), f"salto en la numeración de los archivos: falta el punto {n}")
    return Entrega(carpeta, ruta_indice, puntos)


def destino_enlace(crudo):
    """Destino relativo de un enlace, sin `<…>`, `%20`, `./` ni ancla. None si es externo, absoluto o solo un ancla."""
    crudo = crudo[1:-1] if crudo.startswith("<") else crudo
    if re.match(r"^[a-z][a-z0-9+.-]*:", crudo, re.I) or crudo.startswith(("/", "\\")):
        return None
    destino = re.sub(r"^(?:\./)+", "", unquote(re.split(r"[#?]", crudo, maxsplit=1)[0]).replace("\\", "/"))
    return destino or None


def verificar_titulo_indice(entrega, lineas, documento, inf):
    """El primer H1 del índice es el título del documento (DEC-008)."""
    indice = str(entrega.indice)
    for donde, linea, tipo, _ in lineas:
        m = re.match(r"^#\s+(.*?)\s*#*\s*$", linea) if tipo == "texto" and ruta_de(donde) == indice else None
        if m:
            if normalizar(m.group(1)) != documento:
                inf.error(donde, f"el primer H1 del índice debe ser el título del documento: «{m.group(1)}»")
            return
    inf.error(indice, "el índice no tiene el H1 con el título del documento")


def verificar_enlaces_indice(entrega, lineas, inf):
    """El índice enlaza cada punto, en el orden de los archivos, y no enlaza archivos que no existen."""
    indice = str(entrega.indice)
    en_carpeta = {f.name for f in entrega.carpeta.iterdir()}
    puntos = [r.name for _, r in entrega.puntos]
    enlazados = []
    for donde, linea, tipo, _ in lineas:
        if tipo != "texto" or ruta_de(donde) != indice:
            continue
        for m in ENLACE.finditer(re.sub(r"`[^`]*`", "", linea)):
            destino = destino_enlace(m.group(1))
            if destino is None:
                continue
            existe = destino in en_carpeta if "/" not in destino else (entrega.carpeta / destino).exists()
            if not existe:
                inf.error(donde, f"el índice enlaza «{destino}», que no existe")
            elif destino in puntos and destino not in enlazados:
                enlazados.append(destino)
    for nombre in puntos:
        if nombre not in enlazados:
            inf.error(indice, f"el índice no enlaza «{nombre}»")
    if enlazados != [n for n in puntos if n in enlazados]:
        inf.error(indice, "los enlaces del índice no siguen el orden de los archivos")


def verificar_control_versiones_entrega(entrega, lineas, inf):
    """Una sola tabla de control de versiones, en el índice (DEC-010). Se reconoce por sus columnas."""
    indice = str(entrega.indice) if entrega.indice else None
    en_indice = 0
    for donde, cabecera, _ in tablas_markdown(lineas):
        if "version" not in cabecera or "fecha" not in cabecera:
            continue
        if ruta_de(donde) == indice:
            en_indice += 1
        else:
            inf.error(donde, "tabla de control de versiones en un punto: va solo en el índice")
    if indice and en_indice != 1:
        inf.error(indice, f"el índice debe tener exactamente una tabla de control de versiones, y tiene {en_indice}")


def verificar(prompt, archivos, inf, memorias=None, entrega=None):
    verificar_ejes(prompt, inf)
    lineas = bloques(archivos)
    numeros_archivo = entrega.numeros if entrega else {}
    sin_exigir_numero = normalizar(campo_sin_comentario(prompt, "numeracion_textual")) == "ninguna"
    documento = normalizar(prompt.get("documento", ""))
    sin_numerar = SIN_NUMERAR_BASE | {normalizar(s) for s in prompt.get("sin_numerar", []) or []}
    siglas_ok = SIGLAS_BASE | set(prompt.get("siglas_conocidas", []) or [])
    try:
        max_palabras = int(prompt.get("max_palabras_oracion", 25))
    except ValueError:
        max_palabras = 25
    decimal_coma = normalizar(str(prompt.get("decimal", "coma"))) == "coma"
    miles_punto = normalizar(str(prompt.get("miles", ""))) == "punto"
    digital = normalizar(str(prompt.get("medio", "digital"))) in {"digital", "ambos"}
    apa = estilo_leyendas(prompt) == "apa7"
    try:
        niveles = int(prompt.get("niveles_numerados", 3))
    except ValueError:
        niveles = 3

    # Títulos y numeración
    contadores, capitulos, en_numerado, primer_h1 = [0, 0, 0], [], False, True
    ruta_actual, con_h1 = None, set()
    for donde, linea, tipo, _ in lineas:
        ruta = ruta_de(donde)
        punto = numeros_archivo.get(ruta)
        if ruta != ruta_actual:
            ruta_actual = ruta
            if punto is not None:  # Así los saltos entre archivos no generan errores.
                contadores, en_numerado = [punto - 1, 0, 0], False
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", linea) if tipo == "texto" else None
        if not m:
            continue
        nivel, titulo = len(m.group(1)), m.group(2)
        if nivel > 4:
            inf.error(donde, f"título de nivel {nivel}; el máximo es 4: «{titulo}»")
            continue
        if titulo.endswith(".") and not titulo.endswith("..."):
            inf.error(donde, f"el título termina en punto: «{titulo}»")
        # «2 · Requisitos — Parcial (60 %)» (puntos de una auditoría) no es numeración decimal.
        num = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(?!·)(.+)$", titulo)
        nombre = (num.group(2) if num else titulo).rstrip(".")
        if nivel == 1 and primer_h1 and not num and documento and normalizar(nombre) == documento:
            primer_h1 = False
            continue  # título del documento
        primer_h1 = False
        if nivel == 1:
            capitulos.append((donde, normalizar(nombre)))
            if punto is not None:
                con_h1.add(ruta)
                en_numerado = bool(num)
                if not num:
                    contadores = [punto, 0, 0]
                    if not sin_exigir_numero:
                        inf.error(donde, f"el H1 debe llevar el número {punto} de su archivo: «{titulo}»")
                    continue
                if sin_exigir_numero:
                    inf.aviso(donde, f"«{nombre}» lleva número, pero numeracion_textual es ninguna")
                if [int(p) for p in num.group(1).split(".")] != [punto]:
                    inf.error(donde, f"el H1 lleva el número {num.group(1)}; se esperaba {punto}, el número de su archivo")
                    contadores = [punto, 0, 0]
                    continue
            elif normalizar(nombre) in sin_numerar:
                en_numerado = False
                if num:
                    inf.aviso(donde, f"«{nombre}» suele ir sin número")
                continue
            else:
                en_numerado = True
        if nivel == 4 or nivel > niveles:
            continue
        if not num:
            if en_numerado:
                inf.error(donde, f"título sin numeración decimal: «{titulo}»")
            continue
        partes = [int(p) for p in num.group(1).split(".")]
        if len(partes) != nivel:
            inf.error(donde, f"el número {num.group(1)} no corresponde a un título de nivel {nivel}")
            continue
        esperado = contadores[: nivel - 1] + [contadores[nivel - 1] + 1]
        if partes != esperado:
            inf.error(donde, f"numeración {num.group(1)}; se esperaba {'.'.join(map(str, esperado))}")
        contadores = partes + [0] * (3 - nivel)
    if entrega:
        for _, f in entrega.puntos:
            if str(f) not in con_h1:
                inf.error(str(f), "el punto no tiene H1")

    # Estructura exigida por el prompt
    estructura = [normalizar(s) for s in prompt.get("estructura", []) or []]
    presentes = [c for _, c in capitulos]
    faltan = [s for s in estructura if s not in presentes]
    for s in faltan:
        inf.error("estructura", f"falta el capítulo «{s}» exigido por el prompt")
    orden = [c for c in presentes if c in estructura]
    if not faltan and orden != [s for s in estructura if s in orden]:
        inf.aviso("estructura", "los capítulos no siguen el orden del prompt")

    # Tablas, figuras y avisos
    texto_plano = "\n".join(l for _, l, t, _ in lineas if t == "texto")
    numeros = {"Tabla": [], "Figura": []}
    for i, (donde, linea, tipo, lenguaje) in enumerate(lineas):
        if tipo == "texto" and linea.lstrip().startswith("|"):
            sig = lineas[i + 1][1] if i + 1 < len(lineas) else ""
            prev_es_tabla = i > 0 and lineas[i - 1][1].lstrip().startswith("|")
            if not prev_es_tabla and re.match(r"^\s*\|?\s*:?-{3,}", sig):
                n = leyenda_apa(lineas, i, "Tabla") if apa else leyenda_clasica(siguiente_no_vacia(lineas, i, -1), "Tabla")
                if n is not None:
                    numeros["Tabla"].append((donde, n))
                elif apa:
                    inf.error(donde, "tabla sin la leyenda APA 7 antes: «**Tabla N**» y en la línea siguiente «*Título*»")
                else:
                    inf.error(donde, "tabla sin la línea «**Tabla N.** Título» antes")
        es_imagen = tipo == "texto" and re.search(r"!\[(.*?)\]\(", linea)
        es_mermaid = tipo == "fin_codigo" and lenguaje == "mermaid"
        if es_imagen and not es_imagen.group(1).strip():
            (inf.error if digital else inf.aviso)(donde, "imagen sin texto alternativo")
        if es_imagen or es_mermaid:
            if apa:
                inicio = i
                if es_mermaid:
                    while inicio > 0 and lineas[inicio][2] != "inicio_codigo":
                        inicio -= 1
                n = leyenda_apa(lineas, inicio, "Figura")
            else:
                n = leyenda_clasica(siguiente_no_vacia(lineas, i, 1), "Figura")
            if n is not None:
                numeros["Figura"].append((donde, n))
            elif apa:
                inf.error(donde, "figura sin la leyenda APA 7 antes: «**Figura N**» y en la línea siguiente «*Título*»")
            else:
                inf.error(donde, "figura sin la línea «**Figura N.** Título» después")
        aviso = re.match(r"^>\s*\*\*([^*]+?)[.:]\*\*", linea) if tipo == "texto" else None
        if aviso and normalizar(aviso.group(1)) not in AVISOS:
            inf.aviso(donde, f"aviso «{aviso.group(1)}» fuera de los tipos Nota, Consejo, Advertencia, Peligro")
        elif tipo == "texto" and re.match(r"^>\s*(Nota|Consejo|Advertencia|Peligro|Importante)\s*:", linea, re.I):
            inf.aviso(donde, "el aviso debe escribirse como «> **Nota.** texto»")

    # Con `multiarchivo`, cada archivo numera por su cuenta y con su prefijo, y la mención se busca en él (DEC-009).
    textos = {}
    if entrega:
        for donde, l, t, _ in lineas:
            if t == "texto":
                textos.setdefault(ruta_de(donde), []).append(l)
    for clase, lista in numeros.items():
        cuenta = {}
        for donde, n in lista:
            ruta = ruta_de(donde) if entrega else ""
            cuenta[ruta] = cuenta.get(ruta, 0) + 1
            punto = numeros_archivo.get(ruta)
            esperado = f"{punto}.{cuenta[ruta]}" if punto is not None else str(cuenta[ruta])
            if n != esperado:
                inf.error(donde, f"{clase} {n}: la numeración no es continua; se esperaba {clase} {esperado}")
            texto = "\n".join(textos.get(ruta, [])) if entrega else texto_plano
            menciones = re.findall(rf"(?<!\*\*){clase} {re.escape(n)}(?![\d.]*\*\*)(?!\d)(?!\.\d)", texto, re.I)
            if not menciones:
                inf.aviso(donde, f"{clase} {n} no se menciona en el texto")
    verificar_referencias(lineas, numeros, inf)
    if entrega:
        if entrega.indice:
            verificar_titulo_indice(entrega, lineas, documento, inf)
            verificar_enlaces_indice(entrega, lineas, inf)
        verificar_control_versiones_entrega(entrega, lineas, inf)
    if usa_tablas_estadisticas(prompt):
        verificar_estadistica(lineas, decimal_coma, inf)
    tipos_tabla = {normalizar(str(t)) for t in prompt.get("tablas", []) or []}
    if tipos_tabla & {"endpoints", "riesgos", "trazabilidad"}:
        verificar_tecnicas(lineas, tipos_tabla, inf)
    verificar_academicos(lineas, set(prompt.get("componentes", []) or []), numeros, inf)
    verificar_prologo(lineas, inf)
    propios = {normalizar(str(c)) for c in prompt.get("componentes_plantilla", []) or []}
    if propios:
        verificar_plantilla(lineas, propios, prompt, inf)
    if memorias is not None:
        verificar_memoria(lineas, memorias, inf)

    # Siglas, números, pendientes y oraciones
    vistas = set()
    parrafo, inicio = [], None
    oraciones_largas = []

    def cerrar_parrafo():
        if not parrafo:
            return
        texto = " ".join(parrafo)
        texto = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", texto)
        texto = re.sub(r"`[^`]*`", "X", texto)
        for oracion in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡])", texto):
            palabras = len(re.findall(r"\w+", oracion))
            if palabras > max_palabras:
                oraciones_largas.append((inicio, palabras))
        parrafo.clear()

    capitulo_actual, en_cita = "", False
    for donde, linea, tipo, _ in lineas:
        # Las citas en bloque (> sin rótulo de aviso) son texto ajeno: no cuentan para el largo de oración.
        es_cita = tipo == "texto" and linea.lstrip().startswith(">")
        en_cita = es_cita and (en_cita or not ROTULO_AVISO.match(linea.lstrip()))
        es_prosa = tipo == "texto" and linea.strip() and not en_cita and not re.match(r"^\s*(#|\||!\[|<!--)", linea)
        if not es_prosa:
            cerrar_parrafo()
            inicio = None
        if tipo == "texto" and re.match(r"^#\s", linea):
            capitulo_actual = normalizar(re.sub(r"^#\s+(\d+\.?\s+)?", "", linea).rstrip("."))
        if tipo != "texto" or re.match(r"^#", linea):
            continue
        sin_codigo = re.sub(r"`[^`]*`", "", linea)
        sin_codigo = re.sub(r"\]\([^)]*\)", "]", sin_codigo)
        sin_codigo = re.sub(r"^\s*\*\*\d+(?:\.\d+)*\*\*", "", sin_codigo)  # número de pregunta: **1.2**
        for m in re.finditer(r"(?<![\w-])([A-ZÁÉÍÓÚÑ]{2,6})s?(?![\w-])", sin_codigo):
            sigla = m.group(1)
            if sigla in vistas or sigla in siglas_ok or ROMANOS.match(sigla):
                continue
            vistas.add(sigla)
            antes, despues = sin_codigo[: m.start()], sin_codigo[m.end():]
            if not (antes.endswith("(") or despues.lstrip().startswith("(")):
                inf.aviso(donde, f"la sigla {sigla} no se desarrolla en su primera aparición")
        if decimal_coma and capitulo_actual != "control de versiones":
            for m in re.finditer(r"(?<![\w.,])(\d+)\.(\d+)(?![\w.])", sin_codigo):
                if miles_punto and re.fullmatch(r"\d{1,3}\.\d{3}", m.group(0)):
                    continue
                if not CONTEXTO_NUMERO.search(sin_codigo[: m.start()]):
                    miles = "punto" if miles_punto else "espacio"
                    inf.aviso(donde, f"«{m.group(0)}»: usa coma decimal o {miles} para miles")
        for m in re.finditer(r"\d%", sin_codigo):
            inf.aviso(donde, "falta un espacio antes de «%»")
        if "[PENDIENTE" in linea.upper():
            inf.info.append(f"{donde}: {linea.strip()}")
        if es_prosa:
            if inicio is None:
                inicio = donde
            parrafo.append(re.sub(r"^\s*(?:[-*+]|\d+\.|>)\s*", "", linea.strip()))
            if re.match(r"^\s*(?:[-*+]|\d+\.)\s", linea):
                cerrar_parrafo()
                inicio = None
    cerrar_parrafo()
    for donde, palabras in oraciones_largas:
        inf.aviso(donde, f"oración de {palabras} palabras (máximo {max_palabras})")


def es_inventario_figuras(ruta):
    """`figuras/inventario.md` es una hoja de trabajo de la traducción de imágenes, no parte del documento."""
    return ruta.name.lower() == "inventario.md" and ruta.resolve().parent.name.lower() == "figuras"


def main():
    p = argparse.ArgumentParser(description="Verifica documentación Markdown contra un prompt de estilo.")
    p.add_argument("--prompt", required=True, help="ruta al prompt-estilo.md")
    p.add_argument("rutas", nargs="+", help="archivos .md o carpetas con el documento; con entrega: multiarchivo, una sola carpeta")
    p.add_argument("--memoria-agente", help="memoria del agente (por defecto, memoria/decisiones.md de documentacion-estilo)")
    p.add_argument("--memoria-proyecto", help="memoria del proyecto (por defecto, decisiones-estilo.md junto al prompt)")
    a = p.parse_args()
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")

    prompt_ruta = Path(a.prompt)
    if not prompt_ruta.is_file():
        print(f"ERROR: no existe el prompt {prompt_ruta}", file=sys.stderr)
        return 2
    prompt, _, _ = leer_frontmatter(prompt_ruta.read_text(encoding="utf-8"))
    faltan = [k for k in ("documento", "tipo", "metodologia", "medio", "tratamiento", "salida", "estructura") if not prompt.get(k)]
    if faltan:
        print(f"ERROR: al prompt le faltan los campos: {', '.join(faltan)}", file=sys.stderr)
        return 2

    inf = Informe()
    try:
        entrega = preparar_entrega(prompt, [Path(r) for r in a.rutas], prompt_ruta, inf)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    archivos = list(entrega.archivos) if entrega else []
    for r in map(Path, [] if entrega else a.rutas):
        if r.is_dir():
            archivos += sorted(f for f in r.rglob("*.md") if f.resolve() != prompt_ruta.resolve() and not es_inventario_figuras(f))
        elif r.is_file():
            archivos.append(r)
        else:
            print(f"ERROR: no existe {r}", file=sys.stderr)
            return 2
    if not archivos and not entrega:
        print("ERROR: no se encontraron archivos .md", file=sys.stderr)
        return 2

    agente = Path(a.memoria_agente) if a.memoria_agente else Path(__file__).resolve().parents[2] / "documentacion-estilo" / "memoria" / "decisiones.md"
    proyecto = Path(a.memoria_proyecto) if a.memoria_proyecto else prompt_ruta.parent / "decisiones-estilo.md"
    memorias = {"DEC": leer_memoria(agente), "DP": leer_memoria(proyecto)}

    verificar(prompt, archivos, inf, memorias, entrega)
    print(f"Documento: {prompt.get('documento')} | archivos: {len(archivos)}")
    for titulo, lista in (("ERRORES", inf.errores), ("ADVERTENCIAS", inf.advertencias), ("PENDIENTES", inf.info)):
        print(f"\n{titulo} ({len(lista)})")
        for item in lista:
            print(f"  - {item}")
    print("\nResultado:", "con errores" if inf.errores else "sin errores")
    return 1 if inf.errores else 0


if __name__ == "__main__":
    sys.exit(main())
