// Syntaxe de tout le JavaScript de web/ (27/11/2026) : node --test tests/web/*.test.mjs
// Chaque fichier .js et chaque <script> ecrit dans une page doit se lire (comme « node --check ») : une virgule en
// trop casse toute une page sans rien dire. vendor/ exclu (bibliotheques d'autres projets, telechargees a l'installation).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const WEB = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'installation', 'web');
function fichiers(dossier) {
  return fs.readdirSync(dossier, { withFileTypes: true }).flatMap(e => {
    const p = path.join(dossier, e.name);
    if (e.name === 'vendor') return [];
    return e.isDirectory() ? fichiers(p) : /\.(html|js)$/.test(e.name) ? [p] : [];
  });
}

for (const f of fichiers(WEB)) {
  const rel = path.relative(WEB, f), src = fs.readFileSync(f, 'utf8');
  const morceaux = f.endsWith('.js') ? [src] : [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
  if (!morceaux.length) continue;
  test('syntaxe : ' + rel, () => {
    morceaux.forEach((code, i) => {
      assert.doesNotThrow(() => new vm.Script(code, { filename: rel + (f.endsWith('.html') ? ' <script> n° ' + (i + 1) : '') }));
    });
  });
}
