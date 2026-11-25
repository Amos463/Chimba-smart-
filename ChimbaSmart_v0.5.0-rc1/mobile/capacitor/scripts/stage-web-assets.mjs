import { copyFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const projectDir = path.resolve(scriptDir, '../../..');
const frontendDir = path.join(projectDir, 'frontend');
const webDir = path.resolve(scriptDir, '../www');
const assets = [
  'index.html',
  'app.js',
  'capacitor-bridge.js',
  'field-workflows.js',
  'style.css',
  'manifest.json',
  'sw.js',
  'icon.svg',
];

await mkdir(webDir, { recursive: true });
await Promise.all(assets.map(asset => copyFile(
  path.join(frontendDir, asset),
  path.join(webDir, asset),
)));
