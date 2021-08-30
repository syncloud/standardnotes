#!/bin/sh -e

VERSION=3.8.18
DIR=$(pwd)
BUILD_DIR=$DIR/build/notes
cd ${BUILD_DIR}

apk add --update --no-cache alpine-sdk python2 git yarn tzdata
git clone https://github.com/standardnotes/web.git
cd web
git checkout ${VERSION}
git submodule update --init --force --remote
yarn install --pure-lockfile
yarn bundle

cp -r dist ${BUILD_DIR}/web
cp -r public/* ${BUILD_DIR}/web
cp -r ${DIR}/web/index.html ${BUILD_DIR}/web
