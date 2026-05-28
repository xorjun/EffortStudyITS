import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createAdminServices } from '../shared/clients.js';
import { DATABASE_ID } from '../shared/constants.js';
import { ID, IndexType } from '../shared/sdk.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '../../..');

function buildSdkIndexType(type) {
  switch (type) {
    case 'unique':
      return IndexType.Unique;
    case 'fulltext':
      return IndexType.Fulltext;
    case 'key':
    default:
      return IndexType.Key;
  }
}

function buildSdkOrder(order) {
  return String(order || 'ASC').toUpperCase() === 'DESC' ? 'DESC' : 'ASC';
}

function createAttributeMethod(databases, attribute) {
  const base = {
    databaseId: DATABASE_ID,
    collectionId: attribute.collectionId,
    key: attribute.key,
    required: attribute.required,
  };

  switch (attribute.type) {
    case 'boolean':
      return databases.createBooleanAttribute({ ...base, default: attribute.default, array: false });
    case 'datetime': {
      const payload = { ...base, array: false };
      if (attribute.default !== null && attribute.default !== undefined) {
        payload.default = attribute.default;
      }
      return databases.createDatetimeAttribute(payload);
    }
    case 'float': {
      const payload = { ...base, array: false };
      if (attribute.default !== null && attribute.default !== undefined) {
        payload.default = attribute.default;
      }
      return databases.createFloatAttribute(payload);
    }
    case 'integer': {
      const payload = { ...base, array: false };
      if (attribute.default !== null && attribute.default !== undefined) {
        payload.default = attribute.default;
      }
      return databases.createIntegerAttribute(payload);
    }
    case 'string': {
      const payload = {
        ...base,
        size: attribute.size,
        array: false,
        encrypt: false,
      };
      if (attribute.default !== null && attribute.default !== undefined) {
        payload.default = attribute.default;
      }
      return databases.createStringAttribute(payload);
    }
    default:
      throw new Error(`Unsupported attribute type: ${attribute.type}`);
  }
}

async function waitForAttribute(databases, collectionId, key) {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try {
      const attribute = await databases.getAttribute({ databaseId: DATABASE_ID, collectionId, key });
      if (attribute.status === 'available') {
        return attribute;
      }
      if (attribute.status === 'failed') {
        throw new Error(`Attribute ${collectionId}.${key} failed to build: ${attribute.error}`);
      }
    } catch (error) {
      if (error.code !== 404) {
        throw error;
      }
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  console.warn(`Timed out waiting for attribute ${collectionId}.${key}; continuing schema sync while Appwrite finishes provisioning it.`);
  return null;
}

async function waitForIndex(databases, collectionId, key) {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try {
      const index = await databases.getIndex({ databaseId: DATABASE_ID, collectionId, key });
      if (index.status === 'available') {
        return index;
      }
      if (index.status === 'failed') {
        throw new Error(`Index ${collectionId}.${key} failed to build: ${index.error}`);
      }
    } catch (error) {
      if (error.code !== 404) {
        throw error;
      }
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  console.warn(`Timed out waiting for index ${collectionId}.${key}; continuing schema sync while Appwrite finishes provisioning it.`);
  return null;
}

async function ensureDatabase(databases, databaseConfig) {
  try {
    await databases.get({ databaseId: databaseConfig.id });
  } catch (error) {
    if (error.code !== 404) {
      throw error;
    }
    await databases.create({
      databaseId: databaseConfig.id,
      name: databaseConfig.name,
      enabled: true,
    });
  }
}

async function ensureCollection(databases, collectionConfig) {
  try {
    await databases.getCollection({ databaseId: DATABASE_ID, collectionId: collectionConfig.id });
  } catch (error) {
    if (error.code !== 404) {
      throw error;
    }
    await databases.createCollection({
      databaseId: DATABASE_ID,
      collectionId: collectionConfig.id,
      name: collectionConfig.name,
      permissions: collectionConfig.permissions,
      documentSecurity: collectionConfig.documentSecurity,
      enabled: true,
    });
  }

  const attributeList = await databases.listAttributes({ databaseId: DATABASE_ID, collectionId: collectionConfig.id });
  const existingAttributes = new Set(attributeList.attributes.map((attribute) => attribute.key));

  for (const attribute of collectionConfig.attributes) {
    if (!existingAttributes.has(attribute.key)) {
      await createAttributeMethod(databases, { ...attribute, collectionId: collectionConfig.id });
    }
    await waitForAttribute(databases, collectionConfig.id, attribute.key);
  }

  const indexList = await databases.listIndexes({ databaseId: DATABASE_ID, collectionId: collectionConfig.id });
  const existingIndexes = new Set(indexList.indexes.map((index) => index.key));

  for (const index of collectionConfig.indexes) {
    if (!existingIndexes.has(index.key)) {
      await databases.createIndex({
        databaseId: DATABASE_ID,
        collectionId: collectionConfig.id,
        key: index.key,
        type: buildSdkIndexType(index.type),
        attributes: index.attributes,
        orders: index.orders.map(buildSdkOrder),
      });
    }
    await waitForIndex(databases, collectionConfig.id, index.key);
  }
}

async function ensureBucket(storage, bucketConfig) {
  try {
    await storage.getBucket({ bucketId: bucketConfig.id });
  } catch (error) {
    if (error.code !== 404) {
      throw error;
    }
    await storage.createBucket({
      bucketId: bucketConfig.id,
      name: bucketConfig.name,
      permissions: bucketConfig.permissions,
      fileSecurity: bucketConfig.fileSecurity,
      enabled: bucketConfig.enabled,
      maximumFileSize: bucketConfig.maximumFileSize,
      allowedFileExtensions: bucketConfig.allowedFileExtensions,
      compression: bucketConfig.compression,
      encryption: bucketConfig.encryption,
      antivirus: bucketConfig.antivirus,
      transformations: false,
    });
  }
}

async function ensureTeam(teams, teamConfig) {
  try {
    await teams.get({ teamId: teamConfig.id });
  } catch (error) {
    if (error.code !== 404) {
      throw error;
    }
    await teams.create({ teamId: teamConfig.id, name: teamConfig.name, roles: [] });
  }
}

async function ensureSeeds(databases, config) {
  for (const [collectionId, documents] of Object.entries(config.database.seeds || {})) {
    for (const seed of documents) {
      await databases.upsertDocument({
        databaseId: DATABASE_ID,
        collectionId,
        documentId: seed.documentId || ID.unique(),
        data: seed.data,
        permissions: [],
      });
    }
  }
}

async function main() {
  const configPath = path.join(repoRoot, 'appwrite.json');
  const config = JSON.parse(await fs.readFile(configPath, 'utf8'));
  const { databases, storage, teams } = createAdminServices();

  await ensureDatabase(databases, config.database);

  for (const collection of config.database.collections) {
    await ensureCollection(databases, collection);
  }

  for (const bucket of config.buckets || []) {
    await ensureBucket(storage, bucket);
  }

  for (const team of config.teams || []) {
    await ensureTeam(teams, team);
  }

  await ensureSeeds(databases, config);
  console.log('Appwrite schema sync complete.');
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
