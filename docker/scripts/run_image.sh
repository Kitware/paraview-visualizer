#!/usr/bin/env bash
docker run --rm --gpus all -p 8080:80 \
    -v "$HOME:/data" \
    -d \
    pv-visualizer