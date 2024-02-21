from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver
import json
import config


def main():
    # Setup the Chrome Driver
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    token = gettoken(driver=driver)


def gettoken(driver=None):
    driver.implicitly_wait(0.5)
    driver.maximize_window()
    driver.get(config.sunpower_idp_url)
    driver.save_screenshot('prelogin.png')
    driver.find_element(By.ID, "okta-signin-username").clear()
    driver.find_element(By.ID, "okta-signin-username").send_keys(config.sunpower_email)
    # driver.save_screenshot('username.png')
    driver.find_element(By.ID, "okta-signin-password").clear()
    driver.find_element(By.ID, "okta-signin-password").send_keys(config.sunpower_password)
    # driver.save_screenshot('password.png')
    btn = driver.find_element(By.ID, "okta-signin-submit")
    driver.execute_script ("arguments[0].click();",btn)
    wait = WebDriverWait(driver, 20)
    wait.until(EC.title_is("mySunPower Monitoring"))
    for request in driver.requests:
        data = request.body
        if len(data.decode()) == 0:
            pass
        else:
            try:
                jsondata = json.loads(data.decode())
                if 'accessToken' in jsondata.keys():
                    writetoken(token=jsondata['accessToken'])
                else:
                    pass
            except Exception as e:
                pass


def writetoken(token=None):
    fh = open('.token', 'w')
    fh.write(token)
    fh.close()
    return


if __name__ == "__main__":
    main()
