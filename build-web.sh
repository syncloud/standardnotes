#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

STANDARD_NOTES_WEB_VERSION=3.8.18

BUILD_DIR=${DIR}/build/notes
cd ${BUILD_DIR}
git clone https://github.com/standardnotes/web.git
cd web
git checkout ${STANDARD_NOTES_WEB_VERSION}
git submodule update --init --force --remote
npm install --unsafe-perm
npm install yarn --global
yarn bundle
cd ${DIR}

#cp -r ${DIR}/build/node_modules/standard-notes-web/dist ${BUILD_DIR}/web
cp -r ${DIR}/build/web/dist ${BUILD_DIR}/web
cp -r ${DIR}/build/web/public/* ${BUILD_DIR}/web
cp -r ${DIR}/web/index.html ${BUILD_DIR}/web