#!/usr/bin/env python3
"""Verifica documentación Markdown contra un prompt de estilo de documentacion-estilo.

Uso:
    python3 verificar_doc.py --prompt docs/prompt-estilo.md docs/manual/
    python3 verificar_doc.py --prompt docs/prompt-estilo.md docs/manual/01-intro.md docs/manual/02-uso.md

Revisa estructura, numeración de títulos, tablas, figuras, avisos, siglas,
números y largo de oraciones. Si el prompt declara tablas estadísticas
(`tablas:`), también revisa las reglas de APA 7 (cero inicial, separador
decimal y nota de los asteriscos). Termina con código 1 si encuentra errores.
Solo usa la biblioteca estándar.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

SIN_NUMERAR_BASE = {
    "control de versiones", "portada", "resumen", "abstract", "agradecimientos",
    "dedicatoria", "indice", "indice general", "indice de figuras", "indice de tablas",
    "lista de siglas y abreviaturas", "siglas y abreviaturas", "glosario",
    "referencias", "bibliografia", "anexos", "apendices",
}
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


def leyenda_clasica(linea, clase):
    """«**Tabla N.** Título» en una sola línea. Devuelve N o None."""
    m = re.match(rf"^\*{{0,2}}{clase} (\d+)\.", linea[1].strip()) if linea else None
    return int(m.group(1)) if m else None


def leyenda_apa(lineas, i, clase):
    """APA 7: «**Tabla N**» y en la línea siguiente «*Título*», justo antes del elemento i. Devuelve N o None."""
    j = i - 1
    while j >= 0 and not lineas[j][1].strip():
        j -= 1
    if j < 0 or not re.match(r"^(\*|_)[^*_].*(\*|_)$", lineas[j][1].strip()):
        return None
    numero = siguiente_no_vacia(lineas, j, -1)
    m = re.match(rf"^\*\*{clase} (\d+)\*\*$", numero[1].strip()) if numero else None
    return int(m.group(1)) if m else None


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
        for m in re.finditer(r"(?<!\*\*)(?<!\w)(Tabla|Figura) (\d+)(?![\d.]*\*\*)(?![\d\w])", sin_codigo, re.I):
            clase, n = m.group(1).capitalize(), int(m.group(2))
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


def verificar(prompt, archivos, inf, memorias=None):
    verificar_ejes(prompt, inf)
    lineas = bloques(archivos)
    documento = normalizar(prompt.get("documento", ""))
    sin_numerar = SIN_NUMERAR_BASE | {normalizar(s) for s in prompt.get("sin_numerar", []) or []}
    siglas_ok = SIGLAS_BASE | set(prompt.get("siglas_conocidas", []) or [])
    try:
        max_palabras = int(prompt.get("max_palabras_oracion", 25))
    except ValueError:
        max_palabras = 25
    decimal_coma = normalizar(str(prompt.get("decimal", "coma"))) == "coma"
    digital = normalizar(str(prompt.get("medio", "digital"))) in {"digital", "ambos"}
    apa = estilo_leyendas(prompt) == "apa7"

    # Títulos y numeración
    contadores, capitulos, en_numerado, primer_h1 = [0, 0, 0], [], False, True
    for donde, linea, tipo, _ in lineas:
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", linea) if tipo == "texto" else None
        if not m:
            continue
        nivel, titulo = len(m.group(1)), m.group(2)
        if nivel > 4:
            inf.error(donde, f"título de nivel {nivel}; el máximo es 4: «{titulo}»")
            continue
        if titulo.endswith(".") and not titulo.endswith("..."):
            inf.error(donde, f"el título termina en punto: «{titulo}»")
        num = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.+)$", titulo)
        nombre = (num.group(2) if num else titulo).rstrip(".")
        if nivel == 1 and primer_h1 and not num and documento and normalizar(nombre) == documento:
            primer_h1 = False
            continue  # título del documento
        primer_h1 = False
        if nivel == 1:
            capitulos.append((donde, normalizar(nombre)))
            if normalizar(nombre) in sin_numerar:
                en_numerado = False
                if num:
                    inf.aviso(donde, f"«{nombre}» suele ir sin número")
                continue
            en_numerado = True
        if nivel == 4:
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

    for clase, lista in numeros.items():
        for k, (donde, n) in enumerate(lista, start=1):
            if n != k:
                inf.error(donde, f"{clase} {n}: la numeración no es continua; se esperaba {clase} {k}")
            menciones = re.findall(rf"(?<!\*\*){clase} {n}(?![\d.]*\*\*)(?!\d)", texto_plano, re.I)
            if not menciones:
                inf.aviso(donde, f"{clase} {n} no se menciona en el texto")
    verificar_referencias(lineas, numeros, inf)
    if usa_tablas_estadisticas(prompt):
        verificar_estadistica(lineas, decimal_coma, inf)
    tipos_tabla = {normalizar(str(t)) for t in prompt.get("tablas", []) or []}
    if tipos_tabla & {"endpoints", "riesgos", "trazabilidad"}:
        verificar_tecnicas(lineas, tipos_tabla, inf)
    verificar_academicos(lineas, set(prompt.get("componentes", []) or []), numeros, inf)
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
                if not CONTEXTO_NUMERO.search(sin_codigo[: m.start()]):
                    inf.aviso(donde, f"«{m.group(0)}»: usa coma decimal o espacio para miles")
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


def main():
    p = argparse.ArgumentParser(description="Verifica documentación Markdown contra un prompt de estilo.")
    p.add_argument("--prompt", required=True, help="ruta al prompt-estilo.md")
    p.add_argument("rutas", nargs="+", help="archivos .md o carpetas con el documento")
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

    archivos = []
    for r in map(Path, a.rutas):
        if r.is_dir():
            archivos += sorted(f for f in r.rglob("*.md") if f.resolve() != prompt_ruta.resolve())
        elif r.is_file():
            archivos.append(r)
        else:
            print(f"ERROR: no existe {r}", file=sys.stderr)
            return 2
    if not archivos:
        print("ERROR: no se encontraron archivos .md", file=sys.stderr)
        return 2

    agente = Path(a.memoria_agente) if a.memoria_agente else Path(__file__).resolve().parents[2] / "documentacion-estilo" / "memoria" / "decisiones.md"
    proyecto = Path(a.memoria_proyecto) if a.memoria_proyecto else prompt_ruta.parent / "decisiones-estilo.md"
    memorias = {"DEC": leer_memoria(agente), "DP": leer_memoria(proyecto)}

    inf = Informe()
    verificar(prompt, archivos, inf, memorias)
    print(f"Documento: {prompt.get('documento')} | archivos: {len(archivos)}")
    for titulo, lista in (("ERRORES", inf.errores), ("ADVERTENCIAS", inf.advertencias), ("PENDIENTES", inf.info)):
        print(f"\n{titulo} ({len(lista)})")
        for item in lista:
            print(f"  - {item}")
    print("\nResultado:", "con errores" if inf.errores else "sin errores")
    return 1 if inf.errores else 0


if __name__ == "__main__":
    sys.exit(main())
