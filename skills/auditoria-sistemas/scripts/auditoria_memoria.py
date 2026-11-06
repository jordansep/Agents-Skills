"""Memoria de errores de auditoria-sistemas. Se usa a través de auditoria_lotes.py; el procedimiento está en
references/memoria-errores.md.

Dos niveles: lo personal queda en un archivo fuera del repo y las reglas compartidas, en memoria/reglas.json del
skill. Ninguno guarda datos del objetivo ni del usuario. El control es estricto y por lista blanca: sólo pasan las
palabras de memoria/vocabulario.txt, porque un filtro que busca lo que parece sensible nunca es completo. Rechaza en
lugar de limpiar: una lección a medio limpiar puede seguir diciendo de qué auditoría salió. Corre también justo antes
de cada escritura. Reduce el riesgo sin eliminarlo, porque con palabras generales todavía se puede describir un caso:
por eso una regla también pasa por la aprobación de una persona.
"""
from __future__ import annotations

import datetime
import getpass
import json
import os
import re
import subprocess
import sys
import unicodedata
import uuid
from pathlib import Path

CATEGORIAS = ("hallazgo_perdido", "falso_positivo", "severidad", "cita", "conteo", "cruce_entre_partes", "imagen",
              "version", "cobertura", "informe", "proceso")
ROLES = ("lector", "verificador", "hilo")
MIN_AUDITORIAS = 2
MAX_REGLAS = 15
LARGO_MAXIMO = 200
TASA_NO_SOSTENIDOS = 0.15
MIN_HALLAZGOS_TASA = 10
MARCA_REGISTRADA = "errores-registrados.txt"
AUTOMATICOS = {
    "alta-tasa-no-sostenidos": ("falso_positivo", "Muchos hallazgos no se sostuvieron al verificarlos."),
    "hallazgos-sin-ubicar": ("cita", "Hubo hallazgos sin página ni línea."),
    "diferencias-entre-pasadas": ("hallazgo_perdido", "Las dos pasadas a ciegas llegaron a resultados distintos."),
}
PATRONES_SENSIBLES = [
    (r"[\w.+-]+@[\w-]+\.[\w.-]+", "un correo"),
    (r"(?i)\b(?:https?://|www\.)", "una dirección web"),
    (r"(?i)\b[a-z]:[\\/]|(?:^|\s)[~.]?[\\/]\w|\w[\\/]\w", "una ruta"),
    (r"(?i)\b[\w-]+\.(?:pdf|docx?|md|txt|py|js|ts|json|ya?ml|html?|xlsx?|pptx?|exe|dll|apk|zip|sql|csv)\b", "un nombre de archivo"),
    (r"\b[A-ZÁÉÍÓÚÑ]{2,}[-_.]?[A-ZÁÉÍÓÚÑ]*[-_.]?\d+\b", "un identificador"),
    (r"(?i)\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,}\b", "un commit o un hash"),
    (r"[«»“”\"`]", "una cita textual"),
    (r"\d{2,}", "una cifra"),
    (r"(?<=[a-záéíóúñ,;:] )[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}", "un nombre propio"),
]


def normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", str(texto))
    return " ".join("".join(c for c in sin_tildes if not unicodedata.combining(c)).lower().split())


def ruta_personal() -> Path:
    return Path(os.environ.get("AUDITORIA_MEMORIA") or Path.home() / ".claude" / "auditoria-sistemas" / "errores.jsonl")


def ruta_repo() -> Path:
    return Path(__file__).resolve().parents[1] / "memoria" / "reglas.json"


def leer_personal() -> list[dict]:
    ruta = ruta_personal()
    if not ruta.exists():
        return []
    registros = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        try:
            registros.append(json.loads(linea))
        except ValueError:
            continue  # una línea cortada no invalida el resto de la memoria
    return registros


def vocabulario() -> set[str]:
    ruta = Path(__file__).resolve().parents[1] / "memoria" / "vocabulario.txt"
    palabras: set[str] = set()
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if not linea.startswith("#"):
            palabras.update(normalizar(linea).split())
    return palabras


def palabra_permitida(palabra: str, permitidas: set[str]) -> bool:
    return palabra in permitidas or (palabra.endswith("s") and palabra[:-1] in permitidas) or (palabra.endswith("es") and palabra[:-2] in permitidas)


def control_estricto(texto: str, vetos: set[str] | None = None) -> str | None:
    """El control de todo lo que se guarda. Dice por qué rechaza y en qué posición, sin repetir el dato."""
    if motivo := motivo_sensible(texto, vetos or set()):
        return motivo
    if not re.fullmatch(r"[^\W\d_]+(?:[\s.,;:()¿?¡!-]+[^\W\d_]+)*[\s.,;:()¿?¡!-]*", texto):
        return "tiene números o signos no permitidos"
    permitidas = vocabulario()
    for posicion, palabra in enumerate(re.findall(r"[^\W\d_]+", normalizar(texto)), 1):
        if not palabra_permitida(palabra, permitidas):
            return f"la palabra {posicion} no está en el vocabulario permitido"
    return None


def control_registro(registro: dict) -> None:
    """Última barrera antes de escribir: ningún camino guarda un campo libre sin pasar por acá."""
    vetos = vetos_personales()
    if registro.get("tipo") == "auditoria":
        if set(registro) != {"tipo", "id", "mes", "conteos", "errores"} or not re.fullmatch(r"[0-9a-f]{32}", str(registro["id"])) \
                or not re.fullmatch(r"\d{4}-\d{2}", str(registro["mes"])):
            sys.exit("Registro rechazado: campos no permitidos. No se guardó nada.")
        if set(registro["conteos"]) - {"hallazgos_verificados", "no_sostenidos", "sin_ubicar", "diferencias"} \
                or not all(type(v) is int for v in registro["conteos"].values()):
            sys.exit("Registro rechazado: conteos no permitidos. No se guardó nada.")
        if problemas := validar_lecciones(registro["errores"], vetos):
            sys.exit("\n".join(problemas))
        if any(set(e) != {"categoria", "clave", "leccion"} for e in registro["errores"]):
            sys.exit("Registro rechazado: campos no permitidos en un error. No se guardó nada.")
    elif registro.get("tipo") == "regla":
        if set(registro) != {"tipo", "clave", "categoria", "rol", "regla"} or registro["rol"] not in ROLES or registro["categoria"] not in CATEGORIAS:
            sys.exit("Regla rechazada: campos no permitidos. No se guardó nada.")
        for campo in ("clave", "regla"):
            if motivo := control_estricto(str(registro[campo]), vetos):
                sys.exit(f"Regla rechazada, {campo}: {motivo}. No se guardó nada.")
    else:
        sys.exit("Registro rechazado: tipo desconocido. No se guardó nada.")


def agregar_personal(registro: dict) -> None:
    control_registro(registro)
    ruta = ruta_personal()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


def leer_repo() -> list[dict]:
    ruta = ruta_repo()
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else []


def vetos_personales() -> set[str]:
    vetos = {getpass.getuser(), Path.home().name}
    for clave in ("user.name", "user.email"):
        try:
            salida = subprocess.run(["git", "config", clave], capture_output=True, encoding="utf-8", check=False).stdout.strip()
        except OSError:
            continue
        vetos.add(salida)
        vetos.update(salida.split())
    return vetos


def vetos_de_trabajo(trabajo: Path | None) -> set[str]:
    """Lo que nombra a este objetivo: archivos, identificadores y nombres registrados, sistema y equipo."""
    if not trabajo:
        return set()
    vetos: set[str] = set()
    for ruta in (trabajo / "fichas").glob("*.json"):
        try:
            ficha = json.loads(ruta.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for hecho in ficha.get("hechos", []):
            if hecho.get("tipo") in ("id", "nombre"):
                vetos.update({str(hecho.get("clave", "")), str(hecho.get("valor", ""))})
    for nombre, campos in (("plan.json", ("foco",)), ("sintesis.json", ("equipo", "sistema"))):
        ruta = trabajo / nombre
        if ruta.exists():
            dato = json.loads(ruta.read_text(encoding="utf-8"))
            vetos.update(str(dato.get(c, "")) for c in campos)
            for lote in dato.get("lotes", []):
                for archivo in lote.get("rangos", {}):
                    vetos.update({archivo, Path(archivo).stem})
    return vetos


def motivo_sensible(texto: str, vetos: set[str]) -> str | None:
    """Por qué no se puede guardar este texto, sin repetir el dato; None si no se detecta nada."""
    if len(texto) > LARGO_MAXIMO:
        return f"pasa de {LARGO_MAXIMO} caracteres"
    for patron, nombre in PATRONES_SENSIBLES:
        if re.search(patron, texto):
            return f"parece tener {nombre}"
    plano = normalizar(texto.replace("-", " "))
    for veto in vetos:
        limpio = normalizar(veto.replace("-", " "))
        if len(limpio) >= 4 and re.search(rf"(?<!\w){re.escape(limpio)}(?!\w)", plano):
            return "coincide con un nombre del objetivo o del usuario"
    return None


def errores_automaticos(trabajo: Path) -> tuple[dict, list[dict]]:
    """Cuenta lo medible de una corrida por lotes. Sólo salen números y textos fijos, nada del objetivo."""
    ruta = trabajo / "revision.json"
    if not ruta.exists():
        return {}, []
    revision = json.loads(ruta.read_text(encoding="utf-8"))
    total = 0
    for archivo in (trabajo / "verifica").glob("V*.json"):
        try:
            total += len(json.loads(archivo.read_text(encoding="utf-8")))
        except ValueError:
            continue
    no_sostenidos = len(revision.get("sin_sostener", []))
    conteos = {"hallazgos_verificados": total, "no_sostenidos": no_sostenidos,
               "sin_ubicar": len(revision.get("sin_ubicar", [])), "diferencias": len(revision.get("diferencias", []))}
    claves = []
    if total >= MIN_HALLAZGOS_TASA and no_sostenidos / total >= TASA_NO_SOSTENIDOS:
        claves.append("alta-tasa-no-sostenidos")
    if conteos["sin_ubicar"]:
        claves.append("hallazgos-sin-ubicar")
    if conteos["diferencias"]:
        claves.append("diferencias-entre-pasadas")
    return conteos, [{"categoria": AUTOMATICOS[c][0], "clave": c, "leccion": AUTOMATICOS[c][1]} for c in claves]


def validar_lecciones(lecciones: list, vetos: set[str]) -> list[str]:
    problemas = []
    for i, leccion in enumerate(lecciones, 1):
        if not isinstance(leccion, dict):
            problemas.append(f"Lección {i}: tiene que ser un objeto.")
            continue
        if leccion.get("categoria") not in CATEGORIAS:
            problemas.append(f"Lección {i}: categoría inválida. Usá: {', '.join(CATEGORIAS)}.")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(leccion.get("clave", ""))) or len(str(leccion.get("clave"))) > 40:
            problemas.append(f"Lección {i}: la clave va en minúsculas con guiones, hasta 40 caracteres.")
        for campo in ("clave", "leccion"):
            if motivo := control_estricto(str(leccion.get(campo, "")), vetos):
                problemas.append(f"Lección {i}, {campo}: {motivo}. Reescribila en general; no se guardó nada.")
        if not str(leccion.get("leccion", "")).strip():
            problemas.append(f"Lección {i}: falta el texto.")
    return problemas


def registrar(a) -> None:
    trabajo = Path(a.trabajo) if a.trabajo else None
    if trabajo and (trabajo / MARCA_REGISTRADA).exists():
        sys.exit("Esta corrida ya está registrada: dos registros contarían como dos auditorías.")
    lecciones = json.loads(Path(a.lecciones).read_text(encoding="utf-8")) if a.lecciones else []
    if not isinstance(lecciones, list):
        sys.exit("Las lecciones son una lista.")
    vetos = vetos_personales() | vetos_de_trabajo(trabajo)
    if problemas := validar_lecciones(lecciones, vetos):
        sys.exit("\n".join(problemas))
    conteos, automaticos = errores_automaticos(trabajo) if trabajo else ({}, [])
    errores = automaticos + [{c: l[c] for c in ("categoria", "clave", "leccion")} for l in lecciones]
    # El id es al azar: distingue auditorías sin decir cuál fue.
    agregar_personal({"tipo": "auditoria", "id": uuid.uuid4().hex, "mes": datetime.date.today().strftime("%Y-%m"),
                      "conteos": conteos, "errores": errores})
    if trabajo:
        (trabajo / MARCA_REGISTRADA).write_text("registrada\n", encoding="utf-8")
    print(f"Registrados {len(errores)} errores en la memoria personal.")


def reglas_activas(rol: str | None = None) -> list[dict]:
    """Las del repo primero: si una clave está en los dos niveles, vale la compartida."""
    reglas, vistas = [], set()
    for regla in leer_repo() + [r for r in leer_personal() if r.get("tipo") == "regla"]:
        if regla.get("clave") not in vistas and (rol is None or regla.get("rol") == rol):
            vistas.add(regla.get("clave"))
            reglas.append(regla)
    return reglas


def bloque_reglas(rol: str) -> str:
    """El texto que suma cada prompt. Cada subagente paga estas líneas: por eso hay un tope de reglas."""
    reglas = reglas_activas(rol)
    if not reglas:
        return ""
    return "\n## Reglas aprendidas de auditorías anteriores\n\n" + "\n".join(f"- {r['regla']}" for r in reglas) + "\n"


def auditorias_por_clave() -> dict[str, dict]:
    claves: dict[str, dict] = {}
    for registro in leer_personal():
        if registro.get("tipo") != "auditoria":
            continue
        for error in registro.get("errores", []):
            dato = claves.setdefault(error["clave"], {"categoria": error["categoria"], "auditorias": set(), "lecciones": []})
            dato["auditorias"].add(registro.get("id"))
            if error["leccion"] not in dato["lecciones"]:
                dato["lecciones"].append(error["leccion"])
    return claves


def propuestas(a) -> None:
    activas = {r.get("clave") for r in reglas_activas()}
    claves = auditorias_por_clave()
    listas = {c: d for c, d in claves.items() if len(d["auditorias"]) >= MIN_AUDITORIAS and c not in activas}
    for clave, dato in sorted(listas.items()):
        print(f"{clave} · {dato['categoria']} · {len(dato['auditorias'])} auditorías")
        for leccion in dato["lecciones"][:3]:
            print(f"  - {leccion}")
    observacion = sum(1 for c, d in claves.items() if len(d["auditorias"]) < MIN_AUDITORIAS and c not in activas)
    print(f"{len(listas)} para proponer · {observacion} en observación · {len(activas)} reglas activas de {MAX_REGLAS}")


def aprobar(a) -> None:
    if a.rol not in ROLES:
        sys.exit(f"El rol es uno de: {', '.join(ROLES)}.")
    dato = auditorias_por_clave().get(a.clave)
    if not dato or len(dato["auditorias"]) < MIN_AUDITORIAS:
        sys.exit(f"Esa clave tiene que aparecer en {MIN_AUDITORIAS} auditorías antes de ser una regla.")
    if motivo := control_estricto(a.regla, vetos_personales()):
        sys.exit(f"Regla rechazada: {motivo}. Reescribila en general; no se guardó nada.")
    if not a.repo and any(r.get("clave") == a.clave for r in reglas_activas()):
        sys.exit("Esa clave ya tiene una regla activa.")
    if a.repo and any(r.get("clave") == a.clave for r in leer_repo()):
        sys.exit("Esa clave ya está en la memoria del skill.")
    if len({r.get("clave") for r in reglas_activas()} | {a.clave}) > MAX_REGLAS:
        sys.exit(f"Ya hay {MAX_REGLAS} reglas activas: retirá una antes de sumar otra.")
    regla = {"clave": a.clave, "categoria": dato["categoria"], "rol": a.rol, "regla": a.regla}
    if a.repo:
        reglas = leer_repo()
        regla = {"id": f"ERR-{len(reglas) + 1:03d}", **regla}
        ruta_repo().parent.mkdir(parents=True, exist_ok=True)
        ruta_repo().write_text(json.dumps(reglas + [regla], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{regla['id']} guardada en la memoria del skill. Subí la versión y envialo con un PR.")
    else:
        agregar_personal({"tipo": "regla", **regla})
        print("Regla activa en la memoria personal. Para compartirla, repetí con --repo desde el repositorio del skill.")


def control(a) -> None:
    """Prueba textos sin guardar nada."""
    trabajo = Path(a.trabajo) if a.trabajo else None
    vetos = vetos_personales() | vetos_de_trabajo(trabajo)
    problemas = validar_lecciones(json.loads(Path(a.lecciones).read_text(encoding="utf-8")), vetos) if a.lecciones else []
    if a.regla and (motivo := control_estricto(a.regla, vetos)):
        problemas.append(f"Regla: {motivo}.")
    if problemas:
        sys.exit("\n".join(problemas))
    print("Control superado. Igual releé el texto: el control no ve todo.")


def agregar_comandos(sub) -> None:
    c = sub.add_parser("errores-control")
    c.add_argument("--trabajo")
    c.add_argument("--lecciones")
    c.add_argument("--regla")
    c.set_defaults(func=control)
    c = sub.add_parser("errores-registrar")
    c.add_argument("--trabajo")
    c.add_argument("--lecciones")
    c.set_defaults(func=registrar)
    c = sub.add_parser("errores-propuestas")
    c.set_defaults(func=propuestas)
    c = sub.add_parser("errores-aprobar")
    c.add_argument("--clave", required=True)
    c.add_argument("--rol", required=True)
    c.add_argument("--regla", required=True)
    c.add_argument("--repo", action="store_true")
    c.set_defaults(func=aprobar)
