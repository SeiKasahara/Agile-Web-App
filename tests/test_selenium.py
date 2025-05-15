# selenium_auth_test.py

import os
import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from dotenv import load_dotenv
from app import create_app
from threading import Thread

def run_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dotenv_path = os.path.join(base_dir, ".env.development")
    load_dotenv(dotenv_path, override=True)


    os.environ.setdefault("FLASK_ENV", "development")

    app = create_app()
    app.run(port=5000, debug=False, use_reloader=False)

class SeleniumAuthTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Thread(target=run_app, daemon=True)
        cls.server.start()
        time.sleep(2)
        cls.base = "http://127.0.0.1:5000"
    
    def setUp(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        # optional: suppress logging
        options.add_argument('--log-level=3')
        options.set_capability('unhandledPromptBehavior', 'accept')

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(3)
        self.driver.get(self.base)

    def tearDown(self):
        self.driver.quit()

    def handle_alert_if_present(self):
        try:
            alert = self.driver.switch_to.alert
            text = alert.text
            alert.accept()
            time.sleep(1)
            return text
        except:
            return None

    def test_1_register_success(self):
        self.driver.get(f"{self.base}/signup")

        self.driver.find_element(By.NAME, "first_name").send_keys("Selenium")
        self.driver.find_element(By.NAME, "last_name").send_keys("User")
        self.driver.find_element(By.NAME, "email").send_keys("selenium_test@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Test@1234")

        self.driver.find_element(By.NAME, "confirm_password").send_keys("Test@1234")

        self.driver.find_element(By.ID, "sign-up-form").submit()
        time.sleep(2)

        alert = self.handle_alert_if_present()
        if alert:
            self.assertIn("account", alert.lower())
        else:
            page = self.driver.page_source.lower()
            url = self.driver.current_url
            self.assertTrue(
                "account" in page or
                "success" in page or
                "/login" in url or
                "login" in page
            )

    def test_2_login_valid_credentials(self):

        self.driver.get(f"{self.base}/signup")
        self.driver.find_element(By.NAME, "first_name").send_keys("Test")
        self.driver.find_element(By.NAME, "last_name").send_keys("User")
        self.driver.find_element(By.NAME, "email").send_keys("login_user@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Login@123")
        self.driver.find_element(By.NAME, "confirm_password").send_keys("Login@123")
        self.driver.find_element(By.ID, "sign-up-form").submit()
        time.sleep(1)


        self.driver.get(f"{self.base}/login")
        self.driver.find_element(By.NAME, "email").send_keys("login_user@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Login@123")

        self.driver.find_element(By.ID, "login-form").submit()
        time.sleep(2)

        alert = self.handle_alert_if_present()
        if alert:
            self.assertIn("login success", alert.lower())
        else:
            page = self.driver.page_source.lower()
            self.assertTrue(
                "logout" in page or
                "dashboard" in page or
                self.driver.current_url != f"{self.base}/login"
            )

    def test_3_login_wrong_password(self):

        self.driver.get(f"{self.base}/signup")
        self.driver.find_element(By.NAME, "first_name").send_keys("Test")
        self.driver.find_element(By.NAME, "last_name").send_keys("User")
        self.driver.find_element(By.NAME, "email").send_keys("wrongpass@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Right@123")
        self.driver.find_element(By.NAME, "confirm_password").send_keys("Right@123")
        self.driver.find_element(By.ID, "sign-up-form").submit()
        time.sleep(1)


        self.driver.get(f"{self.base}/login")
        self.driver.find_element(By.NAME, "email").send_keys("wrongpass@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Nope@123")
        self.driver.find_element(By.ID, "login-form").submit()
        time.sleep(2)

        alert = self.handle_alert_if_present()
        if alert:
            self.assertIn("invalid", alert.lower())
        else:
            self.assertIn("invalid", self.driver.page_source.lower())

    def test_4_logout_redirect(self):

        self.driver.get(f"{self.base}/signup")
        self.driver.find_element(By.NAME, "first_name").send_keys("L")
        self.driver.find_element(By.NAME, "last_name").send_keys("O")
        self.driver.find_element(By.NAME, "email").send_keys("logout@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Logout@123")
        self.driver.find_element(By.NAME, "confirm_password").send_keys("Logout@123")
        self.driver.find_element(By.ID, "sign-up-form").submit()
        time.sleep(1)

        self.driver.get(f"{self.base}/login")
        self.driver.find_element(By.NAME, "email").send_keys("logout@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Logout@123")
        self.driver.find_element(By.ID, "login-form").submit()
        self.handle_alert_if_present()


        self.driver.get(f"{self.base}/logout")
        time.sleep(1)
        self.assertIn("login", self.driver.page_source.lower())

    def test_5_invalid_reset_token(self):

        self.driver.get(f"{self.base}/reset-password/invalidtoken")
        time.sleep(1)

        page = self.driver.page_source.lower()
        self.assertTrue("login" in page or "/login" in self.driver.current_url)

    def test_6_register_missing_fields(self):

        self.driver.get(f"{self.base}/signup")
        self.driver.find_element(By.NAME, "first_name").send_keys("Missing")
        self.driver.find_element(By.NAME, "last_name").send_keys("Field")
        self.driver.find_element(By.NAME, "password").send_keys("Test@1234")
        self.driver.find_element(By.NAME, "confirm_password").send_keys("Test@1234")
        self.driver.find_element(By.ID, "sign-up-form").submit()
        time.sleep(1)

        page = self.driver.page_source.lower()
        self.assertTrue("error" in page or "required" in page or "email" in page)

    def test_7_login_missing_password(self):
        self.driver.get(f"{self.base}/login")
        self.driver.find_element(By.NAME, "email").send_keys("selenium_test@example.com")

        self.driver.find_element(By.ID, "login-form").submit()
        time.sleep(1)

        page = self.driver.page_source.lower()
        self.assertIn("password", page)

    def test_8_direct_access_dashboard_redirects(self):

        self.driver.get(f"{self.base}/dashboard")
        time.sleep(1)

        page = self.driver.page_source.lower()
        self.assertIn("login", page or self.driver.current_url)

if __name__ == '__main__':
    unittest.main()
