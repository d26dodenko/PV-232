import { spawn } from 'node:child_process';
const children = [
  ['back/server.js'],
  ['node_modules/vite/bin/vite.js', '--config', 'front/vite.config.js', '--host', '127.0.0.1'],
].map((args) => spawn(process.execPath, args, { stdio: 'inherit' }));
let stopping = false;
function stop(code) {
  if (stopping) return;
  stopping = true;
  for (const child of children) child.kill('SIGTERM');
  process.exitCode = code;
}
for (const child of children) child.on('exit', (code) => stop(code ?? 1));
process.on('SIGINT', () => stop(0));
process.on('SIGTERM', () => stop(0));
