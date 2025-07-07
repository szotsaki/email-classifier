#!/bin/bash

set -euo pipefail

usage() { >&2 echo "Usage: $0 [-s <socket directory>]"; exit 1; }

socket_dir=/run/email-classifier
while getopts "s:" o; do
  case "${o}" in
    s) socket_dir=${OPTARG} ;;
    *) usage ;;
  esac
done
shift $((OPTIND-1))

if [ -t 0 ]; then
  >&2 echo "This program reads from STDIN. Redirect the e-mail to it."
  exit 1
fi

SOCKET="${socket_dir}"/classify.sock
if [ ! -S "${SOCKET}" ]; then
  >&2 echo "${SOCKET} doesn't exist. Perhaps the classifier isn't running?"
  exit 1
fi

# ASCII 04: End of Transmission. NULL cannot be stored in Bash variables
EMAIL=$(tr -d $'\x04')$'\x04'
echo "${EMAIL}" | socat -t 120 STDIO,ignoreeof UNIX:"${SOCKET}"