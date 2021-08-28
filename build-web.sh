#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

#${DIR}/build/nodejs/bin/npm install standard-notes-web@${STANDARD_NOTES_WEB_VERSION}
git clone https://github.com/standardnotes/web.git
cd web
git checkout ${STANDARD_NOTES_WEB_VERSION}
git submodule update --init --force --remote
${DIR}/build/nodejs/bin/npm install --unsafe-perm
${DIR}/build/nodejs/bin/npm install yarn --global
yarn bundle
cd ${DIR}

#cp -r ${DIR}/build/node_modules/standard-notes-web/dist ${BUILD_DIR}/web
cp -r ${DIR}/build/web/dist ${BUILD_DIR}/web
cp -r ${DIR}/build/web/public/* ${BUILD_DIR}/web
cp -r ${DIR}/web/index.html ${BUILD_DIR}/web