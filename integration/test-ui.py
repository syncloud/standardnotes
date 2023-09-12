from os.path import dirname, join
from subprocess import check_output

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.screenshots import screenshots
from integration import lib
DIR = dirname(__file__)


TMP_DIR = '/tmp/syncloud/ui'


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir, ui_mode, data_dir, app, domain, device_host, local):
    if not local:
        add_host_alias(app, device_host, domain)

        def module_teardown():
            device.activated()
            device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
            device.run_ssh('journalctl > {0}/journalctl.log'.format(TMP_DIR), throw=False)
            device.run_ssh('cp -r {0}/log/*.log {1}'.format(data_dir, TMP_DIR), throw=False)
            device.scp_from_device('{0}/*'.format(TMP_DIR), join(artifact_dir, ui_mode))
            check_output('cp /videos/* {0}'.format(artifact_dir), shell=True)
            check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)
        request.addfinalizer(module_teardown)


def test_start(module_setup):
    pass


def test_index(selenium):
    selenium.open_app()
    selenium.find_by(By.XPATH, "//div[contains(.,'Sign in to sync your notes')]")
    selenium.screenshot('index')


def test_register(selenium, driver, ui_mode, screenshot_dir):
    selenium.click_by(By.XPATH, "//button[contains(., 'Create free account')]")

    selenium.click_by(By.XPATH, "//div[text()='Advanced options']")
    server = selenium.find_by(By.XPATH, "//label[text()='Custom sync server']/following::input").get_attribute('value')
    selenium.screenshot('sync-server')
    assert server == "/api"

    selenium.find_by(By.XPATH, "//input[@type='email']").send_keys('{0}@example.com'.format(ui_mode))
    selenium.find_by(By.XPATH, "//input[@type='password']").send_keys('pass1234')
    selenium.screenshot('new-account')

    selenium.click_by(By.XPATH, "//button[text()='Next']")
    selenium.find_by(By.XPATH, "//input[@type='password']").send_keys('pass1234')

    selenium.click_by(By.XPATH, "//button[contains(., 'Create account')]")
    selenium.screenshot('registered')


def test_logout(selenium):
    selenium.click_by(By.XPATH, "(//footer//button)[1]")
    selenium.find_by(By.XPATH, "//div[text()='Account']")
    selenium.screenshot('signout-before')
    selenium.click_by(By.XPATH, "//button[text()='Sign out workspace']")
    selenium.click_by(By.XPATH, "//button[text()='Sign Out']")
    selenium.find_by(By.XPATH, "//span[text()='Offline']")
    selenium.screenshot('signout-after')


def test_login(selenium):
    #selenium.click_by(By.XPATH, "(//footer//button)[1]")
    lib.login(selenium)


def test_teardown(driver):
    driver.quit()
