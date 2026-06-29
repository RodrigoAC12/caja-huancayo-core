const fs = require("fs");
const path = require("path");

const roots = ["src", "public", "index.html", "vercel.json", "package.json"].filter(fs.existsSync);
const validExt = new Set([".js", ".jsx", ".css", ".html", ".json"]);

const replacements = [
  ["\u00c3\u00a1", "\u00e1"],
  ["\u00c3\u00a9", "\u00e9"],
  ["\u00c3\u00ad", "\u00ed"],
  ["\u00c3\u00b3", "\u00f3"],
  ["\u00c3\u00ba", "\u00fa"],
  ["\u00c3\u00b1", "\u00f1"],
  ["\u00c3\u0081", "\u00c1"],
  ["\u00c3\u0089", "\u00c9"],
  ["\u00c3\u008d", "\u00cd"],
  ["\u00c3\u0093", "\u00d3"],
  ["\u00c3\u009a", "\u00da"],
  ["\u00c3\u0091", "\u00d1"],
  ["\u00c2\u00bf", "\u00bf"],
  ["\u00c2\u00a1", "\u00a1"],
  ["\u00c2\u00b0", "\u00b0"],
  ["\u00c2\u00b7", "\u00b7"],
  ["\u00e2\u0080\u0093", "\u2013"],
  ["\u00e2\u0080\u0094", "\u2014"],
  ["\u00e2\u0080\u0098", "\u2018"],
  ["\u00e2\u0080\u0099", "\u2019"],
  ["\u00e2\u0080\u009c", "\u201c"],
  ["\u00e2\u0080\u009d", "\u201d"],
  ["\u00e2\u0080\u00a6", "\u2026"]
];

function walk(target) {
  const stat = fs.statSync(target);

  if (stat.isFile()) {
    return [target];
  }

  let files = [];
  for (const item of fs.readdirSync(target)) {
    const full = path.join(target, item);
    const itemStat = fs.statSync(full);

    if (itemStat.isDirectory()) {
      files = files.concat(walk(full));
    } else {
      files.push(full);
    }
  }

  return files;
}

let changed = 0;

for (const root of roots) {
  const files = walk(root);

  for (const file of files) {
    const ext = path.extname(file).toLowerCase();

    if (!validExt.has(ext)) continue;

    let content = fs.readFileSync(file, "utf8");
    const original = content;

    for (const [bad, good] of replacements) {
      content = content.split(bad).join(good);
    }

    if (content !== original) {
      fs.writeFileSync(file, content, "utf8");
      console.log("Corregido:", file);
      changed++;
    }
  }
}

console.log("Archivos corregidos:", changed);
