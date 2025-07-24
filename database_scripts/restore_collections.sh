#!/usr/bin/env bash

# Default values
host="localhost"
collections=""
user="useradmin"
password="SECRET"
authDatabase="admin"
dump_location="/home/its/db_backup"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--host)
            host="$2"
            shift 2
            ;;
        -c|--collections)
            collections="$2"
            shift 2
            ;;
        -u|--user)
            user="$2"
            shift 2
            ;;
        -p|--password)
            password="$2"
            shift 2
            ;;
        --auth-database)
            authDatabase="$2"
            shift 2
            ;;
        -l|--location)
            dump_location="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to restore a specific collection
restore_collection() {
    collection="$1"
    echo "Restoring collection: $collection"
    #mongorestore -u "$user" -p "$password" --authenticationDatabase "$authDatabase" --host "$host" --port 27017 --nsInclude="its_db.${collection}" --dir "$dump_location"
    mongorestore -u "$user" -p "$password" --authenticationDatabase "$authDatabase" --host "$host" --port 27017 -d "its_db" --collection="${collection}" --dir "${dump_location}/${collection}.bson"
}

# Check if specific collections are provided
if [ -n "$collections" ]; then
    IFS=',' read -ra collection_array <<< "$collections"
    for collection in "${collection_array[@]}"; do
        restore_collection "$collection"
    done
else
    # Restore the full database
    echo "Restoring the full database"
    mongorestore -u "$user" -p "$password" --authenticationDatabase "$authDatabase" --host "$host" --port 27017 --db "its_db" --dir "$dump_location"
fi

echo "Restore process completed."