#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

VERSION=0.6.6
BUILD_DIR=${DIR}/build/notes
mkdir -p ${BUILD_DIR}
cd ${DIR}/build
wget -c https://github.com/mdouchement/standardfile/archive/refs/tags/v${VERSION}.tar.gz --progress dot:giga
tar xf v${VERSION}.tar.gz
cd standardfile-${VERSION}
go build -ldflags "-s -w -X main.version=${VERSION} -X main.revision=${DRONE_BUILD_NUMBER} -X main.date=$(date +%Y-%m-%d~%H:%M:%S)" -o ${BUILD_DIR}/bin/standardfile cmd/sfc
mkdir ${BUILD_DIR}/bin
tar xf standardfile_${STANDARD_FILES_VERSION}_linux_${STANDARD_FILES_ARCH}.tar.gz -C ${BUILD_DIR}/bin
