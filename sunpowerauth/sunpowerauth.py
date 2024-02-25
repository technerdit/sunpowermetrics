from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver
import json
import config


class SunPowerAuth(object):
    def __init__(self):
        # Setup the Chrome Driver
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)

    def gettoken(self):
        self.driver.implicitly_wait(0.5)
        self.driver.maximize_window()
        self.driver.get(config.sunpower_idp_url)
        self.driver.save_screenshot('prelogin.png')
        self.driver.find_element(By.ID, "okta-signin-username").clear()
        self.driver.find_element(By.ID, "okta-signin-username").send_keys(config.sunpower_email)
        self.driver.find_element(By.ID, "okta-signin-password").clear()
        self.driver.find_element(By.ID, "okta-signin-password").send_keys(config.sunpower_password)
        btn = self.driver.find_element(By.ID, "okta-signin-submit")
        self.driver.execute_script ("arguments[0].click();",btn)
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.title_is("mySunPower Monitoring"))
        for request in self.driver.requests:
            if request.url == "https://sds.mysunpower.com/deal-close/authentication":
                data = request.body
                if len(data.decode()) == 0:
                    pass
                else:
                    try:
                        jsondata = json.loads(data.decode())
                        if 'accessToken' in jsondata.keys():
                            self.__writetoken(token=jsondata['accessToken'])
                            print("Got new access token: {}".format(jsondata['accessToken']))
                            return jsondata['accessToken']
                        else:
                            pass
                    except Exception as e:
                        pass

    def __writetoken(self, token=None):
        fh = open('.token', 'w')
        fh.write(token)
        fh.close()
        return


if __name__ == "__main__":
    spa = SunPowerAuth()
    token = spa.gettoken()
    print(token)
