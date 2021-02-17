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
STANDARD_FILES_VERSION=0.5.0
STANDARD_NOTES_WEB_VERSION=3.5.17
NODE_VERSION=8.11.3
ARCH=$(uname -m)
STANDARD_FILES_ARCH=64-bit
if [[ ${ARCH} == "armv7l" ]]; then
    STANDARD_FILES_ARCH=arm7
fi
SNAP_ARCH=$(dpkg --print-architecture)
VERSION=$2

DOWNLOAD_URL=https://github.com/syncloud/3rdparty/releases/download/1

rm -rf ${DIR}/build
BUILD_DIR=${DIR}/build/${NAME}
mkdir -p ${BUILD_DIR}
cp -r ${DIR}/bin ${BUILD_DIR}

wget --progress=dot:giga ${DOWNLOAD_URL}/python-${ARCH}.tar.gz
tar xf python-${ARCH}.tar.gz
mv python ${BUILD_DIR}

wget --progress=dot:giga ${DOWNLOAD_URL}/nginx-${ARCH}.tar.gz
tar xf nginx-${ARCH}.tar.gz
mv nginx ${BUILD_DIR}/

${BUILD_DIR}/python/bin/pip install -r ${DIR}/requirements.txt

cd ${DIR}/build
DOWNLOAD_URL=https://github.com/tectiv3/standardfile/releases/download
wget ${DOWNLOAD_URL}/v${STANDARD_FILES_VERSION}/standardfile_${STANDARD_FILES_VERSION}_linux_${STANDARD_FILES_ARCH}.tar.gz --progress dot:giga
tar xf standardfile_${STANDARD_FILES_VERSION}_linux_${STANDARD_FILES_ARCH}.tar.gz -C ${BUILD_DIR}/bin

NODE_ARCH=${ARCH}
if [[ ${ARCH} == "x86_64" ]]; then
    NODE_ARCH=x64
fi
NODE_ARCHIVE=node-v${NODE_VERSION}-linux-${NODE_ARCH}
wget https://nodejs.org/dist/v${NODE_VERSION}/${NODE_ARCHIVE}.tar.gz \
    --progress dot:giga
tar xzf ${NODE_ARCHIVE}.tar.gz
mv ${NODE_ARCHIVE} ${DIR}/build/nodejs

export PATH=${DIR}/build/nodejs/bin:$PATH
export LD_LIBRARY_PATH=${DIR}/build/nodejs/lib

#${DIR}/build/nodejs/bin/npm install standard-notes-web@${STANDARD_NOTES_WEB_VERSION}
git clone https://github.com/standardnotes/web.git
cd web
git checkout ${STANDARD_NOTES_WEB_VERSION}
git submodule update --init --force --remote
${DIR}/build/nodejs/bin/npm install
${DIR}/build/nodejs/bin/npm install yarn --global
yarn bundle
cd ${DIR}

cp -r ${DIR}/config ${BUILD_DIR}/config.templates
cp -r ${DIR}/hooks ${BUILD_DIR}
#cp -r ${DIR}/build/node_modules/standard-notes-web/dist ${BUILD_DIR}/web
cp -r ${DIR}/build/web/dist ${BUILD_DIR}/web
cp -r ${DIR}/build/web/public/extensions ${BUILD_DIR}/web
cp -r ${DIR}/web/index.html ${BUILD_DIR}/web

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
