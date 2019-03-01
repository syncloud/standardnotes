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
