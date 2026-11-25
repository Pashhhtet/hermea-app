// Проверка скриптов окна: синтаксис каждого файла и одинаковые ключи текстов в ru / uk / pl.
//   node tools/js_check.js program/app/index.html program/app
const vm = require("vm"), fs = require("fs");
const stub = () => new Proxy(function () {}, { get: (t, k) => k === Symbol.toPrimitive ? () => "" : k === "then" ? undefined : stub(), apply: () => stub(), construct: () => stub(), set: () => true });
const ctx = { console, setTimeout: () => 0, setInterval: () => 0, clearTimeout() {}, clearInterval() {}, __BOOT__: { lang: "ru", theme: "auto", scale: 100 },
  document: stub(), localStorage: { getItem: () => null, setItem() {} }, navigator: { platform: "Mac", userAgent: "Mac", language: "ru" }, location: stub(),
  fetch: () => new Promise(() => {}), matchMedia: () => ({ matches: false, addEventListener() {} }), Notification: stub(), requestAnimationFrame: () => 0,
  addEventListener() {}, Intl, Date, Math, JSON, Object, Array, Set, Map, Promise, RegExp, String, Number, Symbol, Proxy, URL, URLSearchParams, encodeURIComponent, Error };
ctx.window = ctx; vm.createContext(ctx);
const src = fs.readFileSync(process.argv[2], "utf8");
const inl = [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
const files = ["svk.js", "templates.js", "clients.js", "owners.js"].map((f) => fs.readFileSync(process.argv[3] + "/" + f, "utf8"));
let syntaxBad = 0;
const names = ["index.html (встроенный)", ...inl.slice(1).map(() => "index.html"), "svk.js", "templates.js", "clients.js", "owners.js"];
const ext = ["i18n.js", "core.js", "photo.js"].filter((f) => fs.existsSync(process.argv[3] + "/" + f));
const extCode = ext.map((f) => fs.readFileSync(process.argv[3] + "/" + f, "utf8"));
for (const [i, code] of [...inl, ...extCode, ...files].entries()) {
  try { new vm.Script(code); } catch (e) { syntaxBad++; console.log("синтаксис:", [...names.slice(0, inl.length), ...ext, ...names.slice(inl.length)][i] || i, e.message); }
}
if (syntaxBad) process.exit(1);
// top-level const/let are not on the global object: expose L after each chunk
for (const code of [...inl, ...extCode, ...files]) { try { vm.runInContext(code + "\n;globalThis.__L = typeof L !== 'undefined' ? L : globalThis.__L;", ctx); } catch (e) { /* DOM-зависимые места пропускаем */ } }
const L = ctx.__L; if (!L) { console.log("NO L"); process.exit(2); }
const keys = (o) => new Set(Object.keys(o));
const ru = keys(L.ru), uk = keys(L.uk), pl = keys(L.pl); let bad = 0;
for (const [n, s] of [["uk", uk], ["pl", pl]]) { const miss = [...ru].filter((k) => !s.has(k)); if (miss.length) { bad++; console.log("нет в " + n + ":", miss.join(", ")); } }
for (const [n, s] of [["uk", uk], ["pl", pl]]) { const extra = [...s].filter((k) => !ru.has(k)); if (extra.length) { bad++; console.log("лишние в " + n + ":", extra.join(", ")); } }
console.log("ключей ru:", ru.size, bad ? "РАСХОЖДЕНИЯ" : "переводы совпадают"); process.exit(bad ? 1 : 0);
