#!/usr/bin/env bash
set -e

echo "Creating ITS database user..."
mongosh --quiet <<EOF
use admin
db.auth("admin", "${MONGO_INITDB_ROOT_PASSWORD}")
db.createUser({
  user: "${DB_SERVICE_USER:-backend_service_user}",
  pwd: "${DB_SERVICE_PW}",
  roles: [{ role: "readWrite", db: "its_db" }]
})
EOF
echo "ITS database user created."
