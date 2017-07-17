#!/bin/bash

set -e

PROJ_ROOT=${PWD}

cd ${PROJ_ROOT}/dependency/FFmpeg
./mmake.sh
