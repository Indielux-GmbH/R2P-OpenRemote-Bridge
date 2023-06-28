#!/bin/bash
VERSION=$(jq -r .version manifest.json)
IMAGENAME=$(jq -r .imagename manifest.json)
docker run --rm -ti "${IMAGENAME:-r2p-mqtt-tools}:${VERSION:-develop}" /bin/bash
