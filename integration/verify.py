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
from syncloudlib.integration.ssh import run_scp, run_ssh
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


def module_teardown(device_host, data_dir, platform_data_dir, app_dir, log_dir, app):
    platform_log_dir = join(log_dir, 'platform_log')
    os.mkdir(platform_log_dir)
    run_scp('root@{0}:{1}/log/* {2}'.format(device_host, platform_data_dir, platform_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    
    run_ssh(device_host, 'mkdir {0}'.format(TMP_DIR), password=LOGS_SSH_PASSWORD)
    run_ssh(device_host, 'top -bn 1 -w 500 -c > {0}/top.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'ps auxfw > {0}/ps.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'netstat -nlp > {0}/netstat.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'journalctl > {0}/journalctl.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'cp /var/log/syslog {0}/syslog.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'cp {0}/database/*.err {1}/'.format(data_dir, TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'cp /var/log/messages {0}/messages.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)    
    run_ssh(device_host, 'ls -la /snap > {0}/snap.ls.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)    
    run_ssh(device_host, 'ls -la {0}/ > {1}/app.ls.log'.format(app_dir, TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)    
    run_ssh(device_host, 'ls -la {0}/ > {1}/data.ls.log'.format(data_dir, TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)    
    run_ssh(device_host, 'ls -la {0}/wp-content/ > {1}/data.wp-content.ls.log'.format(data_dir, TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)    
    run_ssh(device_host, 'ls -la {0}/database/ > {1}/database.ls.log'.format(data_dir, TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)    
    run_ssh(device_host, 'ls -la {0}/wordpress/ > {1}/wordpress.ls.log'.format(app_dir, TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)  
    run_ssh(device_host, 'ls -la {0}/wp-content.template/ > {1}/wp-content.template.ls.log'.format(app_dir, TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)  
    run_ssh(device_host, 'ls -la {0}/log/ > {1}/log.ls.log'.format(data_dir, TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)  
    run_ssh(device_host, '{0}/bin/wp-cli core is-installed; echo "is installed: $?" > {1}/wp-cli.isinstalled.log'.format(app_dir, TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False, env_vars='SNAP_COMMON={0}'.format(data_dir))
    run_ssh(device_host, '{0}/bin/wp-cli option list > {1}/wp-cli.options.log'.format(app_dir, TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False, env_vars='SNAP_COMMON={0}'.format(data_dir))
    run_ssh(device_host, '{0}/bin/wp-cli --info > {1}/wp-cli.info.log 2>&1'.format(app_dir, TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False, env_vars='SNAP_COMMON={0}'.format(data_dir))  
    run_ssh(device_host, '{0}/bin/wp-cli user list > {1}/wp-cli.user.list.log 2>&1'.format(app_dir, TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False, env_vars='SNAP_COMMON={0}'.format(data_dir))  

    app_log_dir  = join(log_dir, 'log')
    os.mkdir(app_log_dir )
    run_scp('root@{0}:{1}/log/*.log {2}'.format(device_host, data_dir, app_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    run_scp('root@{0}:{1}/* {2}'.format(device_host, TMP_DIR, app_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    

def test_start(module_setup, device_host, app, log_dir):
    shutil.rmtree(log_dir, ignore_errors=True)
    os.mkdir(log_dir)
    add_host_alias(app, device_host)
    print(check_output('date', shell=True))
    run_ssh(device_host, 'date', password=LOGS_SSH_PASSWORD)


def test_activate_device(main_domain, device_host, domain, device_user, device_password, redirect_user, redirect_password):

    response = requests.post('http://{0}:81/rest/activate'.format(device_host),
                             data={'main_domain': main_domain,
                                   'redirect_email': redirect_user,
                                   'redirect_password': redirect_password,
                                   'user_domain': domain,
                                   'device_username': device_user,
                                   'device_password': device_password})
    assert response.status_code == 200, response.text
    global LOGS_SSH_PASSWORD
    LOGS_SSH_PASSWORD = device_password


def test_install(app_archive_path, device_host, app_domain, device_password):
    local_install(device_host, device_password, app_archive_path)
    wait_for_rest(requests.session(), app_domain, '/', 200, 10)

def test_phpinfo(device_host, app_dir, data_dir, device_password):
    run_ssh(device_host, '{0}/bin/php -i > {1}/log/phpinfo.log'.format(app_dir, data_dir),
            password=device_password, env_vars='SNAP_COMMON={0}'.format(data_dir))


def test_index(app_domain):
    response = requests.get('https://{0}'.format(app_domain), verify=False)                          
    assert response.status_code == 200, response.text


#def test_storage_change(device_host, app_dir, data_dir, device_password):
#    run_ssh(device_host, 'SNAP_COMMON={1} {0}/hooks/storage-change > {1}/log/storage-change.log'.format(app_dir, data_dir), password=device_password, throw=False)

def test_upgrade(app_archive_path, device_host, device_password):
    local_install(device_host, device_password, app_archive_path)

def test_remove(device, app):
    response = device.app_remove(app)
    assert response.status_code == 200, response.text


def test_reinstall(app_archive_path, device_host, device_password):
    local_install(device_host, device_password, app_archive_path)
