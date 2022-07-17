#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )
cd ${DIR}
VERSION=$1
BUILD_DIR=${DIR}/build/snap
mkdir -p ${BUILD_DIR}/bin
cd ${DIR}/build/standardfile

go build -ldflags "-s -w -X main.version=${VERSION} -X main.revision=${DRONE_BUILD_NUMBER} -X main.date=$(date +%Y-%m-%d~%H:%M:%S)" -o ${BUILD_DIR}/bin/standardfile cmd/standardfile/main.go
go build -ldflags "-s -w -X main.version=${VERSION} -X main.revision=${DRONE_BUILD_NUMBER} -X main.date=$(date +%Y-%m-%d~%H:%M:%S)" -o ${BUILD_DIR}/bin/sfc cmd/sfc/main.go
