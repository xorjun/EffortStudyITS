import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '../../..');

async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function main() {
  const spec = JSON.parse(await fs.readFile(path.join(repoRoot, 'appwrite.json'), 'utf8'));
  const missing = [];

  for (const definition of spec.functions) {
    const absoluteEntrypoint = path.join(repoRoot, 'appwrite', 'functions', definition.entrypoint);
    if (!(await fileExists(absoluteEntrypoint))) {
      missing.push(definition.entrypoint);
    }
  }

  if (missing.length > 0) {
    console.error('Missing function entrypoints:');
    for (const entrypoint of missing) {
      console.error(` - ${entrypoint}`);
    }
    process.exitCode = 1;
    return;
  }

  console.log('All function entrypoints are present.');
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
