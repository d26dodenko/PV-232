import { spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const mode = process.argv[2];
const run = (command, args, options = {}) => spawnSync(command, args, { stdio: 'inherit', ...options });
let result;
let restore = () => {};
try {
  if (mode === 'unit' || mode === 'e2e') {
    const file = mode === 'unit' ? 'tests/unit/shop.test.js' : 'tests/e2e/shop.spec.js';
    const original = readFileSync(file, 'utf8');
    const before = mode === 'unit' ? 'totalPrice: 6900' : 'Total: 4500 ₽';
    const after = mode === 'unit' ? 'totalPrice: 6901' : 'Total: 4501 ₽';
    if (!original.includes(before)) throw new Error('Demo assertion not found');
    restore = () => writeFileSync(file, original);
    writeFileSync(file, original.replace(before, after));
    result = run('npm', ['run', mode === 'unit' ? 'test:unit' : 'test:e2e']);
  } else if (mode === 'coverage') {
    const file = 'back/demo-uncovered.js';
    if (existsSync(file)) throw new Error('Demo file already exists');
    restore = () => rmSync(file, { force: true });
    writeFileSync(file, Array.from({ length: 60 }, (_, index) => `export function uncovered${index}(value) {\n  return value ? ${index} : -1;\n}\n`).join('\n'));
    result = run('npm', ['run', 'test:unit']);
  } else if (mode === 'security') {
    const dir = mkdtempSync(join(tmpdir(), 'clothify-audit-demo-'));
    restore = () => rmSync(dir, { recursive: true, force: true });
    writeFileSync(join(dir, 'package.json'), JSON.stringify({ name: 'audit-demonstration', version: '1.0.0', private: true, dependencies: { lodash: '4.17.4' } }));
    const install = run('npm', ['install', '--package-lock-only', '--ignore-scripts', '--no-audit', '--cache', join(tmpdir(), 'clothify-npm-cache')], { cwd: dir });
    if (install.status !== 0) throw new Error('Failed to prepare the vulnerable lockfile');
    result = run('node', ['scripts/security.js', dir]);
  } else {
    throw new Error('Mode: unit, coverage, security or e2e');
  }
} finally {
  restore();
}
console.log('Demo finished; original files restored.');
process.exit(result.status ?? 1);
