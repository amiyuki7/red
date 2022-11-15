#!/bin/sh

ERROR_PREFIX="\033[1;4;31m[ERROR]\033[0m"
SUCCESS_PREFIX="\033[1;4;32m[SUCCESS]\033[0m"

command -v python3 &>/dev/null || { echo >&2 "${ERROR_PREFIX} python3 is not" \
	"installed!\nAborting..."; exit 1; }

PY_VERSION=$(python3 -V | cut -d ' ' -f2)
IFS='.' array=($PY_VERSION)

[ ${array[1]} -lt 10 ] && { echo >&2 "${ERROR_PREFIX} Only python 3.10+ is"\
	"supported; current version bound to \`python3\`: ${PY_VERSION}\n" \
	"Aborting..."; exit 1; }

echo "~~~ Creating virtual environment ~~~"
python3 -m venv venv && source ./venv/bin/activate
echo "~~~ Installing dependencies ~~~"
pip install -r requirements.txt --disable-pip-version-check
echo "~~~ Making scripts runnable ~~~"
chmod +x ./*.sh

echo "${SUCCESS_PREFIX} Setup complete!"

exit 0
