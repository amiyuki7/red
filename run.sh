#!/bin/sh

source ./venv/bin/activate

uvicorn src.redqct.app:server --port 8080
