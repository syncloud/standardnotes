import os
import shutil
from os.path import dirname, join
from subprocess import check_output

import pytest
import requests
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.installer import local_install, wait_for_rest, wait_for_platform_web

DEFAULT_DEVICE_PASSWORD = 'syncloud'
LOGS_SSH_PASSWORD = DEFAULT_DEVICE_PASSWORD
DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud'


@pytest.fixture(scope="session")
def module_setup(request, device, data_dir, platform_data_dir, app_dir, log_dir, app):
    request.addfinalizer(lambda: module_teardown(device, data_dir, platform_data_dir, app_dir, log_dir, app))


def module_teardown(device, data_dir, platform_data_dir, app_dir, log_dir, app):
    platform_log_dir = join(log_dir, 'platform_log')
    os.mkdir(platform_log_dir)
    device.scp_from_device('{0}/log/*'.format(platform_data_dir), platform_log_dir)
    
    device.run_ssh('mkdir {0}'.format(TMP_DIR), throw=False)
    device.run_ssh('top -bn 1 -w 500 -c > {0}/top.log'.format(TMP_DIR), throw=False)
    device.run_ssh('ps auxfw > {0}/ps.log'.format(TMP_DIR), throw=False)
    device.run_ssh('netstat -nlp > {0}/netstat.log'.format(TMP_DIR), throw=False)
    device.run_ssh('journalctl > {0}/journalctl.log'.format(TMP_DIR), throw=False)
    device.run_ssh('cp /var/log/syslog {0}/syslog.log'.format(TMP_DIR), throw=False)
    device.run_ssh('cp /var/log/messages {0}/messages.log'.format(TMP_DIR), throw=False)    
    device.run_ssh('ls -la /snap > {0}/snap.ls.log'.format(TMP_DIR), throw=False)    
    device.run_ssh('ls -la {0}/ > {1}/app.ls.log'.format(app_dir, TMP_DIR), throw=False)    
    device.run_ssh('ls -la {0}/ > {1}/data.ls.log'.format(data_dir, TMP_DIR), throw=False)    
    device.run_ssh('ls -la {0}/notes/ > {1}/notes.ls.log'.format(app_dir, TMP_DIR), throw=False)  
    device.run_ssh('ls -la {0}/log/ > {1}/log.ls.log'.format(data_dir, TMP_DIR), throw=False)  
  
    app_log_dir = join(log_dir, 'log')
    os.mkdir(app_log_dir)
    device.scp_from_device('{0}/log/*.log'.format(data_dir), app_log_dir)
    device.scp_from_device('{0}/*'.format(TMP_DIR), app_log_dir)
    

def test_start(module_setup, device, device_host, app, log_dir):
    shutil.rmtree(log_dir, ignore_errors=True)
    os.mkdir(log_dir)
    add_host_alias(app, device_host)
    print(check_output('date', shell=True))
    device.run_ssh('date', retries=20)


def test_activate_device(device, device_host):
    wait_for_platform_web(device_host) 
    response = device.activate()
    assert response.status_code == 200, response.text


def test_install(app_archive_path, device_host, app_domain, device_password):
    local_install(device_host, device_password, app_archive_path)
    wait_for_rest(requests.session(), app_domain, '/auth/params?email=example.com', 200, 10) 

#def test_index(app_domain):
#    response = requests.get('https://{0}'.format(app_domain), verify=False)                          
#    assert response.status_code == 200, response.text


def test_upgrade(app_archive_path, device_host, device_password):
    local_install(device_host, device_password, app_archive_path)

def test_remove(device, app):
    response = device.app_remove(app)
    assert response.status_code == 200, response.text

def test_reinstall(app_archive_path, device_host, device_password):
    local_install(device_host, device_password, app_archive_path)
