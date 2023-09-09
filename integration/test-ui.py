import time
from os.path import dirname, join
from subprocess import check_output

import pytest
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.screenshots import screenshots
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DIR = dirname(__file__)


TMP_DIR = '/tmp/syncloud/ui'


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir, ui_mode, data_dir):
    def module_teardown():
        device.activated()
        device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/journalctl.log'.format(TMP_DIR), throw=False)
        device.run_ssh('cp -r {0}/log/*.log {1}'.format(data_dir, TMP_DIR), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), join(artifact_dir, ui_mode))
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)
    request.addfinalizer(module_teardown)


def test_start(module_setup, app, domain, device_host):
    add_host_alias(app, device_host, domain)


def test_index(selenium):
    selenium.open_app()
    selenium.find_by(By.XPATH, "//div[contains(.,'Sign in to sync your notes')]")
    selenium.screenshot('index')


def test_register(selenium, driver, ui_mode, screenshot_dir):
    # account = "//div[text()='Account']"
    # wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, account)))
    #btn = driver.find_element_by_xpath(account)
    #btn.click()

    selenium.find_by(By.XPATH, "//button[contains(., 'Create free account')]").click()
    
    options = "//div[contains(., 'Advanced options')]"
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, options)))
    selenium.find_by(By.XPATH, options).click()
    
    name = "//input[@type='email']"
    selenium.find_by(By.XPATH, name).send_keys('{0}@example.com'.format(ui_mode))
    selenium.find_by(By.XPATH, "//input[@type='password']").send_keys('pass1234')
    selenium.screenshot('new-account')

    submit = "//button[text()='Register']"
    selenium.find_by(By.XPATH, submit).click()
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.invisibility_of_element_located((By.XPATH, name)))
    selenium.screenshot('registered')


def test_logout(driver, ui_mode, screenshot_dir):
    account = "//div[text()='Account']"
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, account)))
    btn = driver.find_element_by_xpath(account)
    btn.click()

    logout = "//a[text()='Sign out']"
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, logout)))
    btn = driver.find_element_by_xpath(logout)
    btn.click()

    confirm = "(//button[text()='Sign Out'])[2]"
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, confirm)))
    btn = driver.find_element_by_xpath(confirm)
    screenshots(driver, screenshot_dir, 'signout-before-' + ui_mode)
    btn.click()


def test_login(driver, ui_mode, screenshot_dir):
    signin = "//button[text()='Sign In']"
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, signin)))
    driver.find_element_by_xpath(signin).click()

    name = "//input[@name='email']"
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, name)))
    driver.find_element_by_xpath(name).send_keys('{0}@example.com'.format(ui_mode))
    driver.find_element_by_xpath("//input[@name='password']").send_keys('pass1234')

    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, signin)))
    driver.find_element_by_xpath(signin).click()

    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.invisibility_of_element_located((By.XPATH, name)))
    screenshots(driver, screenshot_dir, 'logged-in')


def test_extensions(driver, screenshot_dir):
    driver.find_element_by_xpath("//div[contains(text(),'Extensions')]").click()
    time.sleep(10)
  
    screenshots(driver, screenshot_dir, 'extensions')


def test_teardown(driver):
    driver.quit()


def wait_or_screenshot(driver, ui_mode, screenshot_dir, method):
    wait_driver = WebDriverWait(driver, 30)
    try:
        wait_driver.until(method)
    except Exception as e:
        screenshots(driver, screenshot_dir, 'exception-' + ui_mode)
        raise e
