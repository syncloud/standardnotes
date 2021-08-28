#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

BUILD_DIR=${DIR}/build/notes/python
docker ps -a -q --filter ancestor=python:syncloud --format="{{.ID}}" | xargs docker stop | xargs docker rm || true
docker rmi python:syncloud || true
docker build -f Dockerfile.python -t python:syncloud .
docker create --name=python python:syncloud
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}
docker export python -o python.tar
tar xf python.tar
docker export python
docker rm python
docker rmi python:syncloud
cp ${DIR}/bin/python ${BUILD_DIR}/bin
rm -rf ${BUILD_DIR}/usr/src
