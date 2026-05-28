import { Account, Client, Databases, Functions, Storage, Teams, Users } from './sdk.js';

function isObjectStyleCall(args) {
  return args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
}

function wrapObjectCompat(target, mappers) {
  return new Proxy(target, {
    get(currentTarget, property, receiver) {
      const mapper = mappers[property];
      if (mapper) {
        return (...args) => {
          const nextArgs = isObjectStyleCall(args) ? mapper(args[0]) : args;
          return currentTarget[property](...nextArgs);
        };
      }

      const value = Reflect.get(currentTarget, property, receiver);
      return typeof value === 'function' ? value.bind(currentTarget) : value;
    },
  });
}

function createDatabasesCompat(databases) {
  return wrapObjectCompat(databases, {
    listDocuments: ({ databaseId, collectionId, queries }) => [databaseId, collectionId, queries],
    getDocument: ({ databaseId, collectionId, documentId, queries }) => [databaseId, collectionId, documentId, queries],
    createDocument: ({ databaseId, collectionId, documentId, data, permissions }) => [databaseId, collectionId, documentId, data, permissions],
    updateDocument: ({ databaseId, collectionId, documentId, data, permissions }) => [databaseId, collectionId, documentId, data, permissions],
    deleteDocument: ({ databaseId, collectionId, documentId }) => [databaseId, collectionId, documentId],
    listAttributes: ({ databaseId, collectionId, queries }) => [databaseId, collectionId, queries],
    getAttribute: ({ databaseId, collectionId, key }) => [databaseId, collectionId, key],
    createBooleanAttribute: ({ databaseId, collectionId, key, required, default: defaultValue, array }) => [databaseId, collectionId, key, required, defaultValue, array],
    createDatetimeAttribute: ({ databaseId, collectionId, key, required, default: defaultValue, array }) => [databaseId, collectionId, key, required, defaultValue, array],
    createFloatAttribute: ({ databaseId, collectionId, key, required, default: defaultValue, array }) => [databaseId, collectionId, key, required, undefined, undefined, defaultValue, array],
    createIntegerAttribute: ({ databaseId, collectionId, key, required, default: defaultValue, array }) => [databaseId, collectionId, key, required, undefined, undefined, defaultValue, array],
    createStringAttribute: ({ databaseId, collectionId, key, size, required, default: defaultValue, array, encrypt }) => [databaseId, collectionId, key, size, required, defaultValue, array, encrypt],
    listIndexes: ({ databaseId, collectionId, queries }) => [databaseId, collectionId, queries],
    getIndex: ({ databaseId, collectionId, key }) => [databaseId, collectionId, key],
    createIndex: ({ databaseId, collectionId, key, type, attributes, orders, lengths }) => [databaseId, collectionId, key, type, attributes, orders, lengths],
    get: ({ databaseId }) => [databaseId],
    create: ({ databaseId, name, enabled }) => [databaseId, name, enabled],
    getCollection: ({ databaseId, collectionId }) => [databaseId, collectionId],
    createCollection: ({ databaseId, collectionId, name, permissions, documentSecurity, enabled }) => [databaseId, collectionId, name, permissions, documentSecurity, enabled],
    upsertDocument: ({ databaseId, collectionId, documentId, data, permissions }) => [databaseId, collectionId, documentId, data, permissions],
    incrementDocumentAttribute: ({ databaseId, collectionId, documentId, attribute, value, max }) => [databaseId, collectionId, documentId, attribute, value, max],
  });
}

function createStorageCompat(storage) {
  return wrapObjectCompat(storage, {
    getBucket: ({ bucketId }) => [bucketId],
    createBucket: ({ bucketId, name, permissions, fileSecurity, enabled, maximumFileSize, allowedFileExtensions, compression, encryption, antivirus }) => [bucketId, name, permissions, fileSecurity, enabled, maximumFileSize, allowedFileExtensions, compression, encryption, antivirus],
    listFiles: ({ bucketId, queries, search }) => [bucketId, queries, search],
    deleteFile: ({ bucketId, fileId }) => [bucketId, fileId],
    createFile: ({ bucketId, fileId, file, permissions, onProgress }) => [bucketId, fileId, file, permissions, onProgress],
  });
}

function createTeamsCompat(teams) {
  return wrapObjectCompat(teams, {
    get: ({ teamId }) => [teamId],
    create: ({ teamId, name, roles }) => [teamId, name, roles],
  });
}

function createAccountCompat(account) {
  return wrapObjectCompat(account, {
    createJWT: () => [],
  });
}

function getProjectId() {
  return process.env.APPWRITE_PROJECT_ID || process.env.APPWRITE_FUNCTION_PROJECT_ID;
}

function getEndpoint() {
  return process.env.APPWRITE_ENDPOINT || 'https://cloud.appwrite.io/v1';
}

export function createAdminClient(req) {
  const client = new Client()
    .setEndpoint(getEndpoint())
    .setProject(getProjectId());

  if (process.env.APPWRITE_API_KEY) {
    client.setKey(process.env.APPWRITE_API_KEY);
    return client;
  }

  const dynamicKey = req?.headers?.['x-appwrite-key'];
  if (dynamicKey) {
    client.setKey(dynamicKey);
    return client;
  }

  throw new Error('Missing Appwrite admin key.');
}

export function createAdminServices(req) {
  const client = createAdminClient(req);
  return {
    client,
    databases: createDatabasesCompat(new Databases(client)),
    storage: createStorageCompat(new Storage(client)),
    users: new Users(client),
    teams: createTeamsCompat(new Teams(client)),
    functions: new Functions(client),
  };
}

export function createUserClient(userJwt) {
  if (!userJwt) {
    throw new Error('Missing user JWT.');
  }

  return new Client()
    .setEndpoint(getEndpoint())
    .setProject(getProjectId())
    .setJWT(userJwt);
}

export function createUserServices(userJwt) {
  const client = createUserClient(userJwt);
  return {
    client,
    account: createAccountCompat(new Account(client)),
    databases: createDatabasesCompat(new Databases(client)),
    storage: createStorageCompat(new Storage(client)),
    teams: createTeamsCompat(new Teams(client)),
    functions: new Functions(client),
  };
}
