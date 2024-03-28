#!/usr/bin/env bash
set -e
dir_path=$(dirname $(realpath $0))
cwd_path=$(pwd)

if [[ "$*" == "update" ]]; then
  echo "Checking for update"
  /usr/bin/env bash -ex -c "cd ${dir_path} && poetry update"
fi

cd ${dir_path} && poetry run bash -e -c "cd \"${cwd_path}\" && python3 \"${dir_path}/main.py\" ${*}"

