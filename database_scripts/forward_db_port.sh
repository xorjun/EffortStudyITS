#!/bin/bash

# Set default values
ssh_host="techfak-its"
local_port=27018
remote_port=27017

# Parse command line options
while getopts ":h:p:r:" opt; do
  case $opt in
    h)
      ssh_host="$OPTARG"
      ;;
    p)
      local_port="$OPTARG"
      ;;
    r)
      remote_port="$OPTARG"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

# Perform SSH tunneling
ssh -L "$local_port":localhost:"$remote_port" "$ssh_host"
