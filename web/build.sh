#!/bin/sh -e

VERSION=3.172.13
DIR=$(pwd)
BUILD_DIR=$DIR/build/snap
cd ${DIR}/build

apk add --update --no-cache alpine-sdk python3 yarn tzdata
wget 'https://github.com/standardnotes/app/archive/refs/tags/@standardnotes/web@$VERSION.tar.gz' web.tar.gz
tar xf web.tar.gz
cd app--standardnotes-web-$VERSION
sed -i '#https://api.standardnotes.com#/api#' packages/web/src/index.html
yarn install
yarn build:web
cp -r packages/web/dist ${BUILD_DIR}/web
