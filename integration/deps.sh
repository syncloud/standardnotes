#!/bin/bash -e

apt-get update
apt-get install -y sshpass openssh-client
pip install -r requirements.txt
