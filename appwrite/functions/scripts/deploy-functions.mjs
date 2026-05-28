import fs from 'node:fs';
import fsp from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import archiver from 'archiver';
import { Client, Functions } from 'node-appwrite';
import { InputFile } from 'node-appwrite/file';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '../../..');
const functionsRoot = path.resolve(__dirname, '..');
const VARIABLE_SPECS = [
  { key: 'APPWRITE_API_KEY', secret: true, required: true },
  { key: 'APPWRITE_PROJECT_ID', secret: false, required: true },
  { key: 'APPWRITE_ENDPOINT', secret: false, required: true },
  { key: 'APPWRITE_DATABASE_ID', secret: false, defaultValue: 'study_db' },
  { key: 'APPWRITE_DOWNLOAD_BUCKET_ID', secret: false, defaultValue: 'download_zips' },
  { key: 'APPWRITE_ADMIN_TEAM_ID', secret: false, defaultValue: 'admins' },
  { key: 'ITS_BASE_URL', secret: false, defaultValue: 'http://localhost:8080' },
  { key: 'SOSCI_BASE_URL', secret: false },
  { key: 'SURVEY_LINK_SECRET', secret: true },
  { key: 'PROLIFIC_COMPLETION_CODE_DAY1_A', secret: false },
  { key: 'PROLIFIC_COMPLETION_CODE_DAY1_B', secret: false },
  { key: 'PROLIFIC_COMPLETION_CODE_FINAL', secret: false },
  { key: 'LLM_API_KEY', secret: true },
  { key: 'LLM_MODEL', secret: false },
];

function requireEnv(name) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }

  return value;
}

async function createArchive() {
  const archivePath = path.join(os.tmpdir(), `its03-appwrite-functions-${Date.now()}.tar.gz`);

  await new Promise((resolve, reject) => {
    const output = fs.createWriteStream(archivePath);
    const archive = archiver('tar', {
      gzip: true,
      gzipOptions: { level: 9 },
    });

    output.on('close', resolve);
    output.on('error', reject);
    archive.on('warning', reject);
    archive.on('error', reject);

    archive.pipe(output);
    archive.glob('**/*', {
      cwd: functionsRoot,
      dot: true,
      ignore: ['node_modules/**', '.tmp/**'],
    });
    archive.finalize().catch(reject);
  });

  return archivePath;
}

function createFunctionsClient() {
  const client = new Client()
    .setEndpoint(requireEnv('APPWRITE_ENDPOINT'))
    .setProject(requireEnv('APPWRITE_PROJECT_ID'))
    .setKey(requireEnv('APPWRITE_API_KEY'));

  return new Functions(client);
}

function loadRequestedIds() {
  const raw = process.env.APPWRITE_FUNCTION_IDS;
  if (!raw) {
    return null;
  }

  return new Set(
    raw
      .split(',')
      .map((value) => value.trim())
      .filter(Boolean),
  );
}

async function loadFunctionDefinitions() {
  const configPath = path.join(repoRoot, 'appwrite.json');
  const config = JSON.parse(await fsp.readFile(configPath, 'utf8'));
  const requestedIds = loadRequestedIds();

  if (!requestedIds) {
    return config.functions;
  }

  const selected = config.functions.filter((definition) => requestedIds.has(definition.id));
  const missing = [...requestedIds].filter((id) => !selected.some((definition) => definition.id === id));

  if (missing.length > 0) {
    throw new Error(`Unknown function ids: ${missing.join(', ')}`);
  }

  return selected;
}

function collectVariables() {
  return VARIABLE_SPECS.flatMap((spec) => {
    const rawValue = process.env[spec.key];
    const value = rawValue ?? spec.defaultValue;

    if (!value) {
      if (spec.required) {
        throw new Error(`Missing required environment variable: ${spec.key}`);
      }
      return [];
    }

    return [{
      key: spec.key,
      value,
      secret: spec.secret,
    }];
  });
}

async function syncVariables(functions, definitions, variables) {
  for (const definition of definitions) {
    const existing = await functions.listVariables(definition.id);
    const existingByKey = new Map(existing.variables.map((variable) => [variable.key, variable]));

    for (const variable of variables) {
      const current = existingByKey.get(variable.key);
      if (current) {
        await functions.updateVariable(definition.id, current.$id, variable.key, variable.value, variable.secret);
        continue;
      }

      await functions.createVariable(definition.id, variable.key, variable.value, variable.secret);
    }

    console.log(`Synced variables for ${definition.id}.`);
  }
}

async function createDeployments(functions, definitions, archivePath) {
  const deployments = [];

  for (const definition of definitions) {
    console.log(`Creating deployment for ${definition.id}...`);
    const deployment = await functions.createDeployment(
      definition.id,
      InputFile.fromPath(archivePath, path.basename(archivePath)),
      true,
      definition.entrypoint,
      definition.commands || undefined,
    );

    console.log(`Queued ${definition.id}: ${deployment.$id} (${deployment.status})`);
    deployments.push({
      functionId: definition.id,
      deploymentId: deployment.$id,
      lastStatus: deployment.status,
    });
  }

  return deployments;
}

async function waitForDeployments(functions, deployments) {
  const pending = new Map(deployments.map((deployment) => [deployment.deploymentId, deployment]));

  while (pending.size > 0) {
    for (const [deploymentId, deployment] of pending) {
      const current = await functions.getDeployment(deployment.functionId, deploymentId);

      if (current.status !== deployment.lastStatus) {
        console.log(`${deployment.functionId}: ${deployment.lastStatus} -> ${current.status}`);
        deployment.lastStatus = current.status;
      }

      if (current.status === 'ready') {
        pending.delete(deploymentId);
        continue;
      }

      if (current.status === 'failed') {
        throw new Error(
          `Deployment failed for ${deployment.functionId}.\n${current.buildLogs || 'No build logs returned.'}`,
        );
      }
    }

    if (pending.size > 0) {
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }
  }
}

async function main() {
  const definitions = await loadFunctionDefinitions();
  if (definitions.length === 0) {
    console.log('No functions selected for deployment.');
    return;
  }

  const functions = createFunctionsClient();
  const variables = collectVariables();
  const archivePath = await createArchive();

  try {
    await syncVariables(functions, definitions, variables);
    const deployments = await createDeployments(functions, definitions, archivePath);
    await waitForDeployments(functions, deployments);
    console.log(`Deployed ${deployments.length} function(s) successfully.`);
  } finally {
    await fsp.rm(archivePath, { force: true });
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});