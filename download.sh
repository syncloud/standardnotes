#!/bin/bash -xe

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

VERSION=$1
DOWNLOAD_URL=https://github.com/syncloud/3rdparty/releases/download
ARCH=$(uname -m)
BUILD_DIR=${DIR}/build/snap

apt update
apt -y install wget unzip

mkdir -p $BUILD_DIR
cd ${DIR}/build

#wget -c https://github.com/cyberb/standardfile/archive/refs/heads/master.tar.gz  --progress dot:giga
#tar xf master.tar.gz
#cd standardfile-master

wget -c https://github.com/mdouchement/standardfile/archive/refs/tags/v${VERSION}.tar.gz --progress dot:giga
tar xf v${VERSION}.tar.gz
mv standardfile-${VERSION} standardfile

#wget -c https://github.com/mdouchement/standardfile/archive/refs/heads/master.tar.gz  --progress dot:giga
#tar xf master.tar.gz
#cd standardfile-master

wget --progress=dot:giga ${DOWNLOAD_URL}/nginx/nginx-${ARCH}.tar.gz
tar xf nginx-${ARCH}.tar.gz
mv nginx ${BUILD_DIR}
