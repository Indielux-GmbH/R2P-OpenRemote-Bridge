#!/bin/bash
echo "=> Getting version"
VERSION=$(jq -r .version manifest.json)
IMAGENAME=$(jq -r .imagename manifest.json)
USERID=$(id -u)
echo "=> Starting docker build"
docker build -t "${IMAGENAME:-r2p-mqtt-tools}:${VERSION:-develop}" -f Dockerfile .

if [[ $1 != "-y" && $1 != "--yes" ]]; then
    read -rp 'Would you like to build the binary? (y\N): ' buildyn
fi

if [[ $buildyn == "Y" || $buildyn == "y" || $1 == "-y" || $1 == "--yes" ]]; then
    echo "=> Building Binary"
    docker run --rm -v ./dist/:/app/code/dist/ "${IMAGENAME:-r2p-mqtt-tools}:${VERSION:-develop}" /bin/bash -c "pyinstaller --onefile --paths /app/code/ /app/code/main.py -y && chown ${USERID}:${USERID} /app/code/dist/main"
fi

echo "=> All Done"
