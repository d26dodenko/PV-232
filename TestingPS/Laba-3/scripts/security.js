import { spawnSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';

mkdirSync('reports', { recursive: true });
const cwd = process.argv[2] ?? process.cwd();
const result = spawnSync('npm', ['audit', '--json'], { cwd, encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 });
let report;
try {
  report = JSON.parse(result.stdout);
  if (result.error || report.error || !report.metadata?.vulnerabilities) throw new Error('Audit did not complete');
} catch {
  console.error('Failed to retrieve the npm audit report', result.stderr);
  process.exit(1);
}
writeFileSync('reports/npm-audit.json', JSON.stringify(report, null, 2));
const { high, critical, moderate, low } = report.metadata.vulnerabilities;
console.log(`npm audit: critical=${critical}, high=${high}, moderate=${moderate}, low=${low}`);
if (critical > 0 || high > 0) process.exit(1);
