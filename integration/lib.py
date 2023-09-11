from selenium.webdriver.common.by import By

def login(selenium, device_user, device_password):
    selenium.find_by(By.XPATH, "//div[contains(.,'Sign in to sync your notes')]")
    selenium.screenshot('upgrade')
