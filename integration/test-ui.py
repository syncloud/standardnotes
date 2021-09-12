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
def module_setup(request, device, artifact_dir, ui_mode):
    def module_teardown():
        device.activated()
        device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/journalctl.ui.{1}.log'.format(TMP_DIR, ui_mode), throw=False)
        device.run_ssh('cp /var/log/syslog {0}/syslog.ui.{1}.log'.format(TMP_DIR, ui_mode), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), join(artifact_dir, 'log'))
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)

    request.addfinalizer(module_teardown)


def test_start(module_setup, app, domain, device_host):
    add_host_alias(app, device_host, domain)


def test_index(driver, app_domain, ui_mode, screenshot_dir):
    driver.get("https://{0}".format(app_domain))
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, "//div[text()='All notes']")))
    screenshots(driver, screenshot_dir, 'index-' + ui_mode)


def test_register(driver, ui_mode, screenshot_dir):
    account = "//div[text()='Account']"
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, account)))
    #btn = driver.find_element_by_xpath(account)
    #btn.click()

    register = "//button[text()='Register']" #version above 3.6
    # register = "//div[contains(@class,'sk-label') and text()='Register']" #version below 3.6
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, register)))
    btn = driver.find_element_by_xpath(register)
    btn.click()

    name = "//input[@name='email']"
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, name)))
    driver.find_element_by_xpath(name).send_keys('user@example.com')
    driver.find_element_by_xpath("//input[@name='password']").send_keys('pass1234')
    driver.find_element_by_xpath("//input[@name='password_conf']").send_keys('pass1234')

    submit = "//button[text()='Register']" #version above 3.6
    # submit = "//div[contains(@class,'sk-label') and text()='Register']" #version below 3.6
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, submit)))
    driver.find_element_by_xpath(submit).click()
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.invisibility_of_element_located((By.XPATH, name)))
    screenshots(driver, screenshot_dir, 'registered-' + ui_mode)


def test_logout(driver, ui_mode, screenshot_dir):
    account = "//div[text()='Account']"
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, account)))
    btn = driver.find_element_by_xpath(account)
    btn.click()

    logout = "//a[text()='Sign out']"
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, logout)))
    btn = driver.find_element_by_xpath(logout)
    btn.click()

    confirm = "//div[text()='Confirm']"
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, confirm)))
    btn = driver.find_element_by_xpath(confirm)
    screenshots(driver, screenshot_dir, 'signout-before-' + ui_mode)
    btn.click()


def test_login(driver, ui_mode, screenshot_dir):
    signin = "//div[contains(@class,'sk-label') and text()='Sign In']"
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, signin)))
    btn = driver.find_element_by_xpath(signin)
    btn.click()

    name = "//input[@name='email']"
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.XPATH, name)))
    driver.find_element_by_xpath(name).send_keys('user@example.com')
    driver.find_element_by_xpath("//input[@name='password']").send_keys('pass1234')

    driver.find_element_by_xpath("//div[contains(@class,'sk-label') and text()='Sign In']").click()
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.invisibility_of_element_located((By.XPATH, name)))
    screenshots(driver, screenshot_dir, 'logged-in')


def test_extensions(driver, screenshot_dir):
    driver.find_element_by_xpath("//div[contains(text(),'Extensions')]").click()
    time.sleep(10)
  
    screenshots(driver, screenshot_dir, 'extensions')


def wait_or_screenshot(driver, ui_mode, screenshot_dir, method):
    wait_driver = WebDriverWait(driver, 30)
    try:
        wait_driver.until(method)
    except Exception as e:
        screenshots(driver, screenshot_dir, 'exception-' + ui_mode)
        raise e
