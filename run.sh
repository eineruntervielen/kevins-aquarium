#!/usr/bin/env bash

set -a
source .env
set +a

RELATIVE_DIR_PATH="$(dirname "${0}")"
FILE="$RELATIVE_DIR_PATH/$DB_PATH"


echo "${FILE}"
if [[ -f "$FILE" ]]; then
  echo "$FILE exists."
else
  touch aquarium.sqlite
  sqlite3 aquarium.sqlite < init.sql
fi
python3 app.py
