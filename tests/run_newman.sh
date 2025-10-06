#!/usr/bin/env bash
set -euo pipefail
COLL="${1:-./tests/Laburen.postman_collection.json}"
ENVF="${2:-./tests/Laburen.postman_environment.json}"
docker run --rm -v "$PWD/tests:/etc/newman" postman/newman \
  run "/etc/newman/$(basename "$COLL")" -e "/etc/newman/$(basename "$ENVF")" --reporters cli
