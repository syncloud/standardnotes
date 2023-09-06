#!/bin/sh -e

VERSION=3.172.5
DIR=$(pwd)
BUILD_DIR=$DIR/build/snap
cd ${DIR}/build

apk add --update --no-cache alpine-sdk python3 git yarn tzdata
git clone https://github.com/standardnotes/web.git src
cd src
git checkout @standardnotes/desktop@${VERSION}
git submodule update --init --force --remote
yarn install
yarn build:web

cp -r packages/web/dist ${BUILD_DIR}/web
#cp -r public/* ${BUILD_DIR}/web
cp -r ${DIR}/web/index.html ${BUILD_DIR}/web
