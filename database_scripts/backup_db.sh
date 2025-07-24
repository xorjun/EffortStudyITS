#!/usr/bin/env bash

# Default values
host="localhost"
database="its_db"
user="backend_service_user"
password="SECRET"
authDatabase="admin"
storageLocation="/home/its/db_backup/"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--host)
            host="$2"
            shift 2
            ;;
        -d|--database)
            database="$2"
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
            storageLocation="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run mongodump with the provided arguments
mongodump -h "$host:27017" -d "${database}" -u "$user" -p "$password" --authenticationDatabase "$authDatabase" -o "$storageLocation"
