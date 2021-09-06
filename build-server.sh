#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

VERSION=0.6.6
VERSION=0.6.6
BUILD_DIR=${DIR}/build/notes
mkdir -p ${BUILD_DIR}/bin
cd ${DIR}/build
wget -c https://github.com/cyberb/standardfile/archive/refs/heads/master.tar.gz  --progress dot:giga
#wget -c https://github.com/mdouchement/standardfile/archive/refs/tags/v${VERSION}.tar.gz --progress dot:giga
#tar xf v${VERSION}.tar.gz
tar xf master.tar.gz
cd standardfile-master
go build -ldflags "-s -w -X main.version=${VERSION} -X main.revision=${DRONE_BUILD_NUMBER} -X main.date=$(date +%Y-%m-%d~%H:%M:%S)" -o ${BUILD_DIR}/bin/standardfile cmd/standardfile/main.go