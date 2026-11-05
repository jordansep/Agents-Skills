// Ejecuta el script del configurador en Node, con un DOM simulado, y genera el prompt
// para los estados que recibe por argumento (JSON: { nombre: estadoParcial | null }).
// Un estado puede traer `__acciones`: lista de [accion, ...args] que se aplican después de cargarlo,
// como lo haría la interfaz: ["esqueleto"], ["mover", zona, nombre, delta], ["alternar", zona, nombre, on],
// ["propio", zona, nombre, regla], ["quitar", zona, nombre], ["capitulos", [títulos]] (botón «usar capítulos»,
// que devuelve el aviso de las partes movidas), ["plantilla", id] (primer paso «Plantilla») y
// ["formato", zona, campo, valor] (formato de una zona, como los selectores de la estructura).
// Para el documento subido: ["entrega", [{ nombre, html }]] (subir varios archivos), ["ir", i] (navegar),
// ["ajuste", i, valores] (ajuste local en el archivo i), ["guardado", objeto] (lo que hay en localStorage),
// ["recargar"] (vuelve a cargar la página con el mismo localStorage), ["indice", nombre] (cambia entrega_indice),
// ["revision"] (lo que falta en toda la entrega), ["inicio"] (numeración del archivo activo) y
// ["capitulos_entrega"] (títulos H1 de toda la entrega), ["cargar", [{ name, texto, repetir, falla }]] (cargarDocumentos con
// archivos simulados y `sanear` y `docxAHtml` simulados), ["confirmar", bool] (respuesta de confirm), ["almacen_falla"]
// (setItem lanza), ["entrega_grande", n] (un archivo de n caracteres), ["llamar", nombre, ...args] (función pura del
// script) y ["restablecer"] (botón «Restablecer»). `avisos` son los avisos mostrados: [texto, falla, duración].
// Uso: node configurador_node.js <configurador.html> '<json>'
// Imprime JSON: { nombre: { prompt, memoria, vista, proposito, ambito, lector, zonas, resultados, aviso_importar, editada,
// documento, reimportado, reexportado }, __catalogo }. `aviso_importar` es el aviso que el importador muestra al cargar
// el estado, `vista` el HTML del ejemplo de la vista previa, `documento` el resumen de la entrega cargada y `reexportado`
// el prompt que sale al importar el generado (solo si el estado trae `entrega`).
"use strict";
const fs = require("fs");
const vm = require("vm");

const html = fs.readFileSync(process.argv[2], "utf8");
const estados = JSON.parse(process.argv[3]);
const codigo = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]).join("\n");

// Objeto que acepta cualquier acceso, llamada o asignación: alcanza para que el script cargue.
function falso(hoja) {
  const f = function () { return p; };
  const p = new Proxy(f, {
    get(t, k) {
      if (k === Symbol.toPrimitive) return () => "";
      if (k === Symbol.iterator) return function* () {};
      if (k === "length") return 0;
      if (k === "then") return undefined;
      // Un solo nivel de hermanos e hijos: los recorridos del DOM terminan.
      if (/^(next|previous)(Element)?Sibling$|^(first|last)(Element)?Child$/.test(String(k))) return hoja ? null : falso(true);
      return p;
    },
    set() { return true; },
    apply() { return p; },
    construct() { return p; }
  });
  return p;
}
const D = falso();
// La hoja de la vista previa guarda el HTML que se le asigna; el resto del DOM es falso.
// Lo que no se asignó responde como el DOM falso (métodos y propiedades que no hacen nada).
const HOJA = new Proxy({ innerHTML: "", offsetWidth: 0, offsetHeight: 0 }, {
  get: (t, k) => (k in t ? t[k] : D[k]),
  set: (t, k, v) => { t[k] = v; return true; }
});
const DOCUMENTO = new Proxy(D, { get: (t, k) => (k === "getElementById" ? id => (id === "doc" ? HOJA : D) : D[k]) });
const almacen = new Map();
let respuestaConfirm = true, almacenFalla = false;
const API = "\n;globalThis.__api = { generarPrompt, generarMemoria, combinar, fijar(v) { S = v; }, estado() { return S; }," +
  " cargarEsqueleto, moverElemento, alternarElemento, agregarPropio, quitarPropio," +
  " capitulos(c) { return aplicarZonas(S, zonasDesdeCapitulos(c)); }, SIN_NUMERAR_BASE," +
  " avisoImportar() { return combinar.aviso; }, CATALOGO_PRE, CATALOGO_POST, aplicarPlantilla, PLANTILLAS, COMPONENTES_PLANTILLA," +
  " formato(z, c, v) { S.formato_zonas[z][c] = v; derivarEstructura(); }, vista() { vistaPrevia(); }," +
  " vaciarEntrega() { fijarEntrega(null); }, irAArchivo, revisarEstructura, inicioNumeracion, capitulosSubidos," +
  " subir(lista) { fijarEntrega({ archivos: ordenarEntrega(lista.map(a => Object.assign({ ajustes: [] }, a))), activo: 0 }); guardarSubido(); return ENTREGA.archivos.map(a => a.nombre); }," +
  " ajuste(i, valores) { ENTREGA.archivos[i].ajustes.push({ id: 'a' + i, bloques: [0], valores, colores: {} }); guardarSubido(); }," +
  " indice(nombre) { S.entrega_indice = nombre; reordenarEntrega(); }," +
  " cargarDocumentos, leyendasPrevias, esperadoLeyenda, h1LlevaNumero(c, s, p) { return h1LlevaNumero(c, new Set(s), p); }, numeroVisible, inlineMd, archivoDeEnlace, separarTitulo," +
  " restablecer() { S = combinar(null); restablecerEntrega(); guardarSubido(); }," +
  " simular() { sanear = h => h; docxAHtml = async () => '<h1>Desde Word</h1>'; globalThis.__avisos = []; aviso = (m, f, ms) => { globalThis.__avisos.push([m, !!f, ms === undefined ? null : ms]); }; }," +
  " avisos() { return globalThis.__avisos; }," +
  " documento() { return ENTREGA && { nombres: ENTREGA.archivos.map(a => a.nombre), activo: ENTREGA.activo, ajustes: ENTREGA.archivos.map(a => a.ajustes.length), inicios: ENTREGA.archivos.map(a => a.html.slice(0, 60)), navegacion: hayNavegacion() }; }, CLAVE_DOC };";
const ctx = {
  document: DOCUMENTO, navigator: D, location: D, URL: D, console,
  localStorage: { getItem: k => (almacen.has(k) ? almacen.get(k) : null), setItem(k, v) { if (almacenFalla) throw new Error("sin lugar"); almacen.set(k, String(v)); }, removeItem(k) { almacen.delete(k); } },
  setTimeout: () => 0, clearTimeout() {}, setInterval: () => 0, clearInterval() {}, requestAnimationFrame: () => 0,
  matchMedia: () => ({ matches: false, addEventListener() {}, addListener() {} }),
  getComputedStyle: () => D, fetch: () => new Promise(() => {}),
  Blob: function () {}, FileReader: function () {}, Image: function () {},
  MutationObserver: function () { return { observe() {}, disconnect() {} }; },
  IntersectionObserver: function () { return { observe() {}, disconnect() {} }; },
  ResizeObserver: function () { return { observe() {}, disconnect() {} }; }
};
ctx.addEventListener = () => {}; ctx.removeEventListener = () => {};
ctx.confirm = () => respuestaConfirm;
ctx.window = ctx; ctx.self = ctx;
// Cargar el script en un contexto nuevo equivale a recargar la página: solo sobrevive el localStorage.
function cargarPagina() {
  const pagina = Object.assign({}, ctx);
  pagina.window = pagina; pagina.self = pagina;
  vm.createContext(pagina);
  vm.runInContext(codigo + API, pagina);
  pagina.__api.simular();
  return pagina.__api;
}
let api = cargarPagina();
const copia = x => JSON.parse(JSON.stringify(x === undefined ? null : x));
const zonas = st => copia({
  pretextuales: st.pretextuales, textual: st.textual, postextuales: st.postextuales, propios: st.propios,
  formato_zonas: st.formato_zonas, estructura: st.estructura, sin_numerar: st.sin_numerar
});
// Archivos con la forma de File que usa cargarDocumentos; `repetir` evita pasar textos enormes por argumento.
const archivoSimulado = ({ name, texto = "", repetir = 0, falla }) => {
  const leer = async valor => { if (falla) throw new Error(falla); return valor; };
  return { name, text: () => leer(texto + "x".repeat(repetir)), arrayBuffer: () => leer(null) };
};
const salida = {};
(async () => {
for (const [nombre, estado] of Object.entries(estados)) {
  const acciones = (estado && estado.__acciones) || [];
  almacen.clear(); api.vaciarEntrega(); api.simular();
  respuestaConfirm = true; almacenFalla = false;
  api.fijar(api.combinar(estado));
  const avisoImportar = api.avisoImportar();
  const resultados = [];
  for (const [accion, ...args] of acciones) {
    let r;
    if (accion === "esqueleto") r = api.cargarEsqueleto();
    else if (accion === "mover") r = api.moverElemento(...args);
    else if (accion === "alternar") r = api.alternarElemento(...args);
    else if (accion === "propio") r = api.agregarPropio(...args);
    else if (accion === "quitar") r = api.quitarPropio(...args);
    else if (accion === "capitulos") r = api.capitulos(...args);
    else if (accion === "plantilla") r = api.aplicarPlantilla(...args);
    else if (accion === "formato") r = api.formato(...args);
    else if (accion === "entrega") r = api.subir(...args);
    else if (accion === "ir") r = api.irAArchivo(...args);
    else if (accion === "ajuste") r = api.ajuste(...args);
    else if (accion === "guardado") almacen.set(api.CLAVE_DOC, JSON.stringify(args[0]));
    else if (accion === "recargar") api = cargarPagina();
    else if (accion === "indice") r = api.indice(...args);
    else if (accion === "revision") r = api.revisarEstructura();
    else if (accion === "inicio") r = api.inicioNumeracion();
    else if (accion === "capitulos_entrega") r = api.capitulosSubidos();
    else if (accion === "cargar") r = await api.cargarDocumentos(args[0].map(archivoSimulado));
    else if (accion === "confirmar") respuestaConfirm = args[0];
    else if (accion === "almacen_falla") almacenFalla = true;
    else if (accion === "entrega_grande") r = api.subir([{ nombre: "grande.md", html: "x".repeat(args[0]) }]);
    else if (accion === "llamar") r = api[args[0]](...args.slice(1));
    else if (accion === "restablecer") r = api.restablecer();
    else throw new Error(`acción desconocida: ${accion}`);
    resultados.push(r === undefined ? null : copia(r));
  }
  const s = api.estado();
  const prompt = api.generarPrompt(), memoria = api.generarMemoria(), documento = copia(api.documento()), avisos = copia(api.avisos());
  HOJA.innerHTML = "";
  s.fuente_vista = "ejemplo";  // La revisión del documento subido necesita un DOM real.
  api.vista();
  const vista = HOJA.innerHTML;
  // Vuelve a importar el prompt generado, igual que el botón «Importar».
  const m = prompt.match(/<!-- configurador:v1 ([\s\S]*?) -->/);
  if (!m) {
    process.stderr.write(`Estado «${nombre}»: el prompt generado no tiene la marca <!-- configurador:v1 … -->.\n`);
    process.exit(1);
  }
  const r = api.combinar(JSON.parse(m[1]));
  let reexportado = null;
  if (estado && estado.entrega) { const copiaR = api.combinar(JSON.parse(m[1])); api.fijar(copiaR); reexportado = api.generarPrompt(); }
  salida[nombre] = {
    prompt, memoria, documento, avisos, reexportado, vista, plantilla: s.plantilla, componentes_plantilla: copia(s.componentes_plantilla), proposito: s.proposito, ambito: s.ambito, lector: s.lector, zonas: zonas(s), resultados,
    aviso_importar: avisoImportar, editada: !!s.estructura_editada,
    reimportado: { proposito: r.proposito, ambito: r.ambito, lector: r.lector, zonas: zonas(r) }
  };
}
salida.__catalogo = copia({ pre: api.CATALOGO_PRE, post: api.CATALOGO_POST, sin_numerar_base: api.SIN_NUMERAR_BASE,
  plantillas: api.PLANTILLAS, componentes_plantilla: api.COMPONENTES_PLANTILLA });
process.stdout.write(JSON.stringify(salida));
})().catch(e => { process.stderr.write(String(e && e.stack || e)); process.exit(1); });
