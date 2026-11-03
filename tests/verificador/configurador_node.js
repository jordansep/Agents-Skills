// Ejecuta el script del configurador en Node, con un DOM simulado, y genera el prompt
// para los estados que recibe por argumento (JSON: { nombre: estadoParcial | null }).
// Un estado puede traer `__acciones`: lista de [accion, ...args] que se aplican después de cargarlo,
// como lo haría la interfaz: ["esqueleto"], ["mover", zona, nombre, delta], ["alternar", zona, nombre, on],
// ["propio", zona, nombre, regla], ["quitar", zona, nombre], ["capitulos", [títulos]] (botón «usar capítulos»,
// que devuelve el aviso de las partes movidas), ["plantilla", id] (primer paso «Plantilla») y
// ["formato", zona, campo, valor] (formato de una zona, como los selectores de la estructura).
// Uso: node configurador_node.js <configurador.html> '<json>'
// Imprime JSON: { nombre: { prompt, vista, proposito, ambito, lector, zonas, resultados, aviso_importar, editada, reimportado },
// __catalogo }. `aviso_importar` es el aviso que el importador muestra al cargar el estado y `vista`, el HTML
// del ejemplo de la vista previa.
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
const ctx = {
  document: DOCUMENTO, navigator: D, location: D, URL: D, console,
  localStorage: { getItem: () => null, setItem() {}, removeItem() {} },
  setTimeout: () => 0, clearTimeout() {}, setInterval: () => 0, clearInterval() {}, requestAnimationFrame: () => 0,
  matchMedia: () => ({ matches: false, addEventListener() {}, addListener() {} }),
  getComputedStyle: () => D, fetch: () => new Promise(() => {}),
  Blob: function () {}, FileReader: function () {}, Image: function () {},
  MutationObserver: function () { return { observe() {}, disconnect() {} }; },
  IntersectionObserver: function () { return { observe() {}, disconnect() {} }; },
  ResizeObserver: function () { return { observe() {}, disconnect() {} }; }
};
ctx.addEventListener = () => {}; ctx.removeEventListener = () => {};
ctx.window = ctx; ctx.self = ctx;
vm.createContext(ctx);
vm.runInContext(codigo + "\n;globalThis.__api = { generarPrompt, combinar, fijar(v) { S = v; }, estado() { return S; }," +
  " cargarEsqueleto, moverElemento, alternarElemento, agregarPropio, quitarPropio," +
  " capitulos(c) { return aplicarZonas(S, zonasDesdeCapitulos(c)); }, SIN_NUMERAR_BASE," +
  " avisoImportar() { return combinar.aviso; }, CATALOGO_PRE, CATALOGO_POST, aplicarPlantilla, PLANTILLAS, COMPONENTES_PLANTILLA," +
  " formato(z, c, v) { S.formato_zonas[z][c] = v; derivarEstructura(); }, vista() { vistaPrevia(); } };", ctx);

const api = ctx.__api;
const copia = x => JSON.parse(JSON.stringify(x === undefined ? null : x));
const zonas = st => copia({
  pretextuales: st.pretextuales, textual: st.textual, postextuales: st.postextuales, propios: st.propios,
  formato_zonas: st.formato_zonas, estructura: st.estructura, sin_numerar: st.sin_numerar
});
const salida = {};
for (const [nombre, estado] of Object.entries(estados)) {
  const acciones = (estado && estado.__acciones) || [];
  api.fijar(api.combinar(estado));
  const avisoImportar = api.avisoImportar();
  const resultados = acciones.map(([accion, ...args]) => {
    let r;
    if (accion === "esqueleto") r = api.cargarEsqueleto();
    else if (accion === "mover") r = api.moverElemento(...args);
    else if (accion === "alternar") r = api.alternarElemento(...args);
    else if (accion === "propio") r = api.agregarPropio(...args);
    else if (accion === "quitar") r = api.quitarPropio(...args);
    else if (accion === "capitulos") r = api.capitulos(...args);
    else if (accion === "plantilla") r = api.aplicarPlantilla(...args);
    else if (accion === "formato") r = api.formato(...args);
    else throw new Error(`acción desconocida: ${accion}`);
    return r === undefined ? null : r;
  });
  const s = api.estado();
  const prompt = api.generarPrompt();
  HOJA.innerHTML = "";
  api.vista();
  const vista = HOJA.innerHTML;
  // Vuelve a importar el prompt generado, igual que el botón «Importar».
  const m = prompt.match(/<!-- configurador:v1 ([\s\S]*?) -->/);
  if (!m) {
    process.stderr.write(`Estado «${nombre}»: el prompt generado no tiene la marca <!-- configurador:v1 … -->.\n`);
    process.exit(1);
  }
  const r = api.combinar(JSON.parse(m[1]));
  salida[nombre] = {
    prompt, vista, plantilla: s.plantilla, componentes_plantilla: copia(s.componentes_plantilla), proposito: s.proposito, ambito: s.ambito, lector: s.lector, zonas: zonas(s), resultados,
    aviso_importar: avisoImportar, editada: !!s.estructura_editada,
    reimportado: { proposito: r.proposito, ambito: r.ambito, lector: r.lector, zonas: zonas(r) }
  };
}
salida.__catalogo = copia({ pre: api.CATALOGO_PRE, post: api.CATALOGO_POST, sin_numerar_base: api.SIN_NUMERAR_BASE,
  plantillas: api.PLANTILLAS, componentes_plantilla: api.COMPONENTES_PLANTILLA });
process.stdout.write(JSON.stringify(salida));
