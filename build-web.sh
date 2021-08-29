#!/bin/sh

VERSION=3.8.18
DIR=$(pwd)
BUILD_DIR=$DIR/build/notes
cd ${BUILD_DIR}

apk add --update --no-cache alpine-sdk nodejs-current python2 git nodejs-npm yarn tzdata
git clone https://github.com/standardnotes/web.git
cd web
git checkout ${VERSION}
git submodule update --init --force --remote
yarn install --pure-lockfile
yarn bundle

#cp -r ${DIR}/build/node_modules/standard-notes-web/dist ${BUILD_DIR}/web
cp -r ${DIR}/build/web/dist ${BUILD_DIR}/web
cp -r ${DIR}/build/web/public/* ${BUILD_DIR}/web
cp -r ${DIR}/web/index.html ${BUILD_DIR}/web
