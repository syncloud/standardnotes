import json
import os
import sys
from os import listdir
from os.path import dirname, join, exists, abspath, isdir
import time
from subprocess import check_output
import pytest
import shutil

from syncloudlib.integration.installer import local_install, wait_for_rest, local_remove, \
    get_data_dir, get_app_dir, get_service_prefix, get_ssh_env_vars
from syncloudlib.integration.loop import loop_device_cleanup
from syncloudlib.integration.ssh import run_scp, device.run_ssh
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration import conftest

import requests


DEFAULT_DEVICE_PASSWORD = 'syncloud'
LOGS_SSH_PASSWORD = DEFAULT_DEVICE_PASSWORD
DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud'


@pytest.fixture(scope="session")
def module_setup(request, device_host, data_dir, platform_data_dir, app_dir, log_dir, app):
    request.addfinalizer(lambda: module_teardown(device_host, data_dir, platform_data_dir, app_dir, log_dir, app))


def module_teardown(device, data_dir, platform_data_dir, app_dir, log_dir, app):
    platform_log_dir = join(log_dir, 'platform_log')
    os.mkdir(platform_log_dir)
    device.scp_from_device('{0}/log/* {1}'.format(platform_data_dir, platform_log_dir))
    
    device.run_ssh('mkdir {0}'.format(TMP_DIR), password=LOGS_SSH_PASSWORD)
    device.run_ssh('top -bn 1 -w 500 -c > {0}/top.log'.format(TMP_DIR))
    device.run_ssh('ps auxfw > {0}/ps.log'.format(TMP_DIR))
    device.run_ssh('netstat -nlp > {0}/netstat.log'.format(TMP_DIR))
    device.run_ssh('journalctl > {0}/journalctl.log'.format(TMP_DIR))
    device.run_ssh('cp /var/log/syslog {0}/syslog.log'.format(TMP_DIR))
    device.run_ssh('cp /var/log/messages {0}/messages.log'.format(TMP_DIR))    
    device.run_ssh('ls -la /snap > {0}/snap.ls.log'.format(TMP_DIR))    
    device.run_ssh('ls -la {0}/ > {1}/app.ls.log'.format(app_dir, TMP_DIR))    
    device.run_ssh('ls -la {0}/ > {1}/data.ls.log'.format(data_dir, TMP_DIR))    
    device.run_ssh('ls -la {0}/notes/ > {1}/notes.ls.log'.format(app_dir, TMP_DIR))  
    device.run_ssh('ls -la {0}/log/ > {1}/log.ls.log'.format(data_dir, TMP_DIR))  
  
    app_log_dir = join(log_dir, 'log')
    os.mkdir(app_log_dir)
    device.scp_from_device('{0}/log/*.log {1}'.format(data_dir, app_log_dir))
    device.scp_from_device('{0}/* {1}'.format(TMP_DIR, app_log_dir))
    

def test_start(module_setup, device_host, app, log_dir):
    shutil.rmtree(log_dir, ignore_errors=True)
    os.mkdir(log_dir)
    add_host_alias(app, device_host)
    print(check_output('date', shell=True))
    device.run_ssh('date', password=LOGS_SSH_PASSWORD)


def test_activate_device(device):
    response = device.activate()
    assert response.status_code == 200, response.text


def test_install(app_archive_path, device_host, app_domain, device_password):
    local_install(device_host, device_password, app_archive_path)
    wait_for_rest(requests.session(), app_domain, '/', 200, 10)


def test_index(app_domain):
    response = requests.get('https://{0}'.format(app_domain), verify=False)                          
    assert response.status_code == 200, response.text


def test_upgrade(app_archive_path, device_host, device_password):
    local_install(device_host, device_password, app_archive_path)

def test_remove(device, app):
    response = device.app_remove(app)
    assert response.status_code == 200, response.text

def test_reinstall(app_archive_path, device_host, device_password):
    local_install(device_host, device_password, app_archive_path)
