#!/usr/bin/env bash
CURRENT_DIR=`dirname "$0"`

# Since Mac doesn't come with realpath by default, let's set the full
# paths using PWD.
pushd .
cd $CURRENT_DIR/..
DEPLOY_DIR=$PWD
popd

docker run --rm --gpus all -p 8080:80 \
    -e TRAME_PARAVIEW=/opt/paraview   \
    -v "$TRAME_PARAVIEW:/opt/paraview" \
    -v "$DEPLOY_DIR:/deploy" \
    -v "$HOME:/data" \
    -d \
    kitware/trame:1.2-glvnd-runtime-ubuntu20.04-py39
