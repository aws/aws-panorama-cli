#!/usr/bin/env bash
set -eo pipefail
DIR=$PWD
BIN=/usr/local/bin
mkdir -p $BIN
rm -f ${BIN}/panorama-cli
ln -s ${DIR}/src/panorama-cli ${BIN}/panorama-cli
chmod +x ${DIR}/src/panorama-cli
echo "Don't delete this directory. Created symlink to panorama-cli in ${BIN}. Run git pull for updates."
echo "Successfully installed panorama-cli"