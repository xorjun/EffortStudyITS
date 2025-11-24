#!/usr/bin/env bash

# Default values
ssh_user="jdannath"
ssh_host="ssh-host"
remote_directory="/home/its/db_backup/"
backup_directory="./"
backup_filename="its_db_backup_$(date +%Y%m%d_%H%M%S)/"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -u|--user)
            ssh_user="$2"
            shift 2
            ;;
        -h|--host)
            ssh_host="$2"
            shift 2
            ;;
        -r|--remote-directory)
            remote_directory="$2"
            shift 2
            ;;
        -b|--backup-directory)
            backup_directory="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run scp with the provided arguments
scp -r "${ssh_user}@${ssh_host}:${remote_directory}" "${backup_directory}${backup_filename}"