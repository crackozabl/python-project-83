#!/usr/bin/env bash

curl -o https://astral.sh/uv/install.sh | sh

source $HOME/.local/bin/env

make install-uv && psql -a -d $DATABASE_URL -f database.sql
