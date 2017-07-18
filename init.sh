#!/bin/bash

set -e

PROJ_ROOT=${PWD}

brew install yasm

cd ${PROJ_ROOT}/dependency/FFmpeg
./mmake.sh

pip3 install pygame
