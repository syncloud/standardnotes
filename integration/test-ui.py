import os
import shutil
from os.path import dirname, join, exists
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.screenshots import screenshots


DIR = dirname(__file__)
screenshot_dir = join(DIR, 'screenshot')

def test_start(app, device_host):
    if exists(screenshot_dir):
        shutil.rmtree(screenshot_dir)
    os.mkdir(screenshot_dir)

    add_host_alias(app, device_host)
    

def test_index(driver, app_domain):

    driver.get("https://{0}".format(app_domain))
    time.sleep(10)
  
    screenshots(driver, screenshot_dir, 'index')
    

def test_login(driver, app_domain, device_user, device_password):

    driver.get("https://{0}/wp-login.php".format(app_domain))
    wait_driver = WebDriverWait(driver, 120)
    wait_driver.until(EC.element_to_be_clickable((By.ID, 'user_login')))

    user = driver.find_element_by_id("user_login")
    user.send_keys(device_user)
    password = driver.find_element_by_id("user_pass")
    password.send_keys(device_password)
    screenshots(driver, screenshot_dir, 'login')
    password.send_keys(Keys.RETURN)
    
    time.sleep(10)
    
    screenshots(driver, screenshot_dir, 'login-complete')
    

def test_admin(driver, app_domain):

    driver.get("https://{0}/wp-admin".format(app_domain))
    time.sleep(10)
    screenshots(driver, screenshot_dir, 'admin')
    

def test_profile(driver, app_domain):

    driver.get("https://{0}/wp-admin/profile.php".format(app_domain))
    time.sleep(10)
    screenshots(driver, screenshot_dir, 'profile')
    

def test_ldap(driver, app_domain):

    driver.get("https://{0}/wp-admin/admin.php?page=mo_ldap_local_login".format(app_domain))
    time.sleep(10)
    screenshots(driver, screenshot_dir, 'ldap')

    
def test_users(driver, app_domain):

    driver.get("https://{0}/wp-admin/users.php".format(app_domain))
    time.sleep(10)
    screenshots(driver, screenshot_dir, 'users')
    
def test_media(driver, app_domain):

    driver.get("https://{0}/wp-admin/media-new.php".format(app_domain))
    time.sleep(2)
    driver.find_element_by_css_selector('p[class="upload-flash-bypass"] a').click()
    file = driver.find_element_by_css_selector('input[id="async-upload"][type="file"]')
    file.send_keys(join(DIR, 'images', 'profile.jpeg'))
    time.sleep(2)
    screenshots(driver, screenshot_dir, 'media')
    save = driver.find_element_by_css_selector('input[id="html-upload"][type="submit"]')
    save.click()
    time.sleep(5)
    screenshots(driver, screenshot_dir, 'media-done')
