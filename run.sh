#!/bin/bash

# gen your ssl key pairs if they dont exist
if [[ ! -f ./certificate.crt ]]; then
    ./scripts/gen_ssl_cert.sh
fi

# run docker compose build/tail/teardown
docker-compose up --build --scale worker=2 -d && docker-compose logs -f julienne && docker-compose down -v --remove-orphans
