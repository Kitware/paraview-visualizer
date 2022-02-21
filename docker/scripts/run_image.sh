#!/usr/bin/env bash

CURRENT_DIR=`dirname "$0"`

cd $CURRENT_DIR/..
DEPLOY_DIR=$PWD

# To capture logs and look at them for debug
# -v "$DEPLOY_DIR/server/logs:/deploy/server/logs" \

docker run -it --rm --gpus all -p 8080:80 \
    -v "$HOME:/data" \
    pv-visualizer