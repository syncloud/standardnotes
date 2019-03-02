#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

if [[ -z "$2" ]]; then
    echo "usage $0 app version"
    exit 1
fi

export TMPDIR=/tmp
export TMP=/tmp

NAME=$1
STANDARD_FILES_VERSION=0.4.1
ARCH=$(uname -m)
STANDARD_FILES_ARCH=64-bit
if [[ ${ARCH} == "armv7l" ]]; then
    STANDARD_FILES_ARCH=arm7
fi
SNAP_ARCH=$(dpkg --print-architecture)
VERSION=$2

DOWNLOAD_URL=http://artifact.syncloud.org/3rdparty

rm -rf ${DIR}/build
BUILD_DIR=${DIR}/build/${NAME}
mkdir -p ${BUILD_DIR}
cp -r ${DIR}/bin ${BUILD_DIR}

cd ${DIR}/build

coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/nginx-${ARCH}.tar.gz
coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/python-${ARCH}.tar.gz

${BUILD_DIR}/python/bin/pip install -r ${DIR}/requirements.txt

cd ${DIR}/build
wget https://github.com/tectiv3/standardfile/releases/download/v${STANDARD_FILES_VERSION}/standardfile_${STANDARD_FILES_VERSION}_linux_${STANDARD_FILES_ARCH}.tar.gz --progress dot:giga
tar xf standardfile_${STANDARD_FILES_VERSION}_linux_${STANDARD_FILES_ARCH}.tar.gz -C ${BUILD_DIR}/bin

cd ${DIR}

cp -r ${DIR}/config ${BUILD_DIR}/config.templates
cp -r ${DIR}/hooks ${BUILD_DIR}

mkdir ${DIR}/build/${NAME}/META
echo ${NAME} >> ${DIR}/build/${NAME}/META/app
echo ${VERSION} >> ${DIR}/build/${NAME}/META/version

echo "snapping"
SNAP_DIR=${DIR}/build/snap
ARCH=$(dpkg-architecture -q DEB_HOST_ARCH)
rm -rf ${DIR}/*.snap
mkdir ${SNAP_DIR}
cp -r ${BUILD_DIR}/* ${SNAP_DIR}/
cp -r ${DIR}/snap/meta ${SNAP_DIR}/
cp ${DIR}/snap/snap.yaml ${SNAP_DIR}/meta/snap.yaml
echo "version: $VERSION" >> ${SNAP_DIR}/meta/snap.yaml
echo "architectures:" >> ${SNAP_DIR}/meta/snap.yaml
echo "- ${ARCH}" >> ${SNAP_DIR}/meta/snap.yaml

PACKAGE=${NAME}_${VERSION}_${ARCH}.snap
echo ${PACKAGE} > ${DIR}/package.name
mksquashfs ${SNAP_DIR} ${DIR}/${PACKAGE} -noappend -comp xz -no-xattrs -all-root
