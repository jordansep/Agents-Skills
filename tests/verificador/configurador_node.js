// Ejecuta el script del configurador en Node, con un DOM simulado, y genera el prompt
// para los estados que recibe por argumento (JSON: { nombre: estadoParcial | null }).
// Uso: node configurador_node.js <configurador.html> '<json>'
// Imprime JSON: { nombre: { prompt, proposito, ambito, lector, reimportado } }.
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
const ctx = {
  document: D, navigator: D, location: D, URL: D, console,
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
vm.runInContext(codigo + "\n;globalThis.__api = { generarPrompt, combinar, fijar(v) { S = v; } };", ctx);

const api = ctx.__api;
const salida = {};
for (const [nombre, estado] of Object.entries(estados)) {
  const s = api.combinar(estado);
  api.fijar(s);
  const prompt = api.generarPrompt();
  // Vuelve a importar el prompt generado, igual que el botón «Importar».
  const m = prompt.match(/<!-- configurador:v1 ([\s\S]*?) -->/);
  if (!m) {
    process.stderr.write(`Estado «${nombre}»: el prompt generado no tiene la marca <!-- configurador:v1 … -->.\n`);
    process.exit(1);
  }
  const r = api.combinar(JSON.parse(m[1]));
  salida[nombre] = {
    prompt, proposito: s.proposito, ambito: s.ambito, lector: s.lector,
    reimportado: { proposito: r.proposito, ambito: r.ambito, lector: r.lector }
  };
}
process.stdout.write(JSON.stringify(salida));
