#!/usr/bin/env bash

echo "Creating mongo users..."
mongo admin --host localhost -u useradmin -p "${MONGO_INITDB_ROOT_PASSWORD}" --eval "db.createUser({user: 'backend_service_user', pwd: '${DB_SERVICE_PW}', roles: [{role: 'readWrite', db: 'its_db'}]});"
echo "Mongo users created."
