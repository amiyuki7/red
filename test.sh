#!/bin/sh

source ./venv/bin/activate

PYTHONPATH=src/ pytest
