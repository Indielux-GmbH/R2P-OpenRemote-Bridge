# An R2P MQTT to OpenenRemote 'bridge'

> **Warning**
>
> This Project was coded for our own usage.
>
> You may use this code but we do not provide any support

This project tries to achive to bridge the gab between our
MQTT Broker and the OpenRemote HiveMQ Broker. OpenRemote will be shorten to `OR` from here.

The OR Broker is limited.

For a full discussion about this see: <https://forum.openremote.io/t/mqtt-agent-external-broker-config/1597>

## Conecpt

- A Python => Docker MQTT Client which subscribes to the device topics
- A sendover to the OpenRemote MQTT Broker with no certs
- On new device detection creating an Asset and Service User

## Requirements

- jq
- Docker

## Findings

- OpenRemote has no python library so we need to do API calls on your own.

## Local Python Virtual Environment

Setup venv:

```bash
virtualenv -p 3.11 .venv
```

Activate venv:

```bash
source source .venv/bin/activate
```

Install requirements:

```bash
pip install -r Docker/app/code/requirements.txt
```

## Using the Binary

When building this project with [build.sh](./build.sh) you will get a docker image and a binary located in [dist/](./dist/) folder.

When using this Binary you still need to provide the [config.ini](./Docker/app/code/config.ini) with all its contents, including the SSL Certs for the MQTT Client.
