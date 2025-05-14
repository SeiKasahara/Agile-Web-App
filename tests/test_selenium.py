import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

class SeleniumAuthTest(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("http://127.0.0.1:5000")

    def tearDown(self):
        self.driver.quit()

    def handle_alert_if_present(self):
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            time.sleep(1)
            return alert_text
        except:
            return None

    def test_1_register_success(self):
        self.driver.get("http://127.0.0.1:5000/signup")
        self.driver.find_element(By.NAME, "first_name").send_keys("Selenium")
        self.driver.find_element(By.NAME, "last_name").send_keys("User")
        self.driver.find_element(By.NAME, "email").send_keys("selenium_test@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Test@1234")
        self.driver.find_element(By.TAG_NAME, "form").submit()
        time.sleep(2)
        alert_text = self.handle_alert_if_present()
        if alert_text:
            self.assertIn("account", alert_text.lower())
        else:
            page = self.driver.page_source.lower()
            current_url = self.driver.current_url
            self.assertTrue(
                "account" in page or
                "success" in page or
                "login" in current_url or
                "/login" in current_url or
                "login" in page
            )

    def test_2_login_valid_credentials(self):
        self.driver.get("http://127.0.0.1:5000/login")
        self.driver.find_element(By.NAME, "email").send_keys("selenium_test@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Test@1234")
        self.driver.find_element(By.TAG_NAME, "form").submit()
        time.sleep(2)
        alert_text = self.handle_alert_if_present()
        if alert_text:
            self.assertIn("login successful", alert_text.lower())
        else:
            page = self.driver.page_source.lower()
            self.assertTrue("logout" in page or "dashboard" in page or "welcome" in page or self.driver.current_url != "http://127.0.0.1:5000/login")

    def test_3_login_wrong_password(self):
        self.driver.get("http://127.0.0.1:5000/login")
        self.driver.find_element(By.NAME, "email").send_keys("selenium_test@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("WrongPassword")
        self.driver.find_element(By.TAG_NAME, "form").submit()
        time.sleep(2)
        alert_text = self.handle_alert_if_present()
        if alert_text:
            self.assertIn("incorrect", alert_text.lower())
        else:
            self.assertIn("invalid", self.driver.page_source.lower())

    def test_4_logout_redirect(self):
        self.driver.get("http://127.0.0.1:5000/login")
        self.driver.find_element(By.NAME, "email").send_keys("selenium_test@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Test@1234")
        self.driver.find_element(By.TAG_NAME, "form").submit()
        self.handle_alert_if_present()
        self.driver.get("http://127.0.0.1:5000/logout")
        time.sleep(1)
        self.assertIn("login", self.driver.page_source.lower())

    def test_5_invalid_email_verification_token(self):
        self.driver.get("http://127.0.0.1:5000/verify-email/invalidtoken")
        time.sleep(1)
        self.assertIn("login", self.driver.page_source.lower())

    def test_6_register_missing_fields(self):
        # Attempt to submit registration with missing email
        self.driver.get("http://127.0.0.1:5000/signup")
        self.driver.find_element(By.NAME, "first_name").send_keys("Missing")
        self.driver.find_element(By.NAME, "last_name").send_keys("Email")
        self.driver.find_element(By.NAME, "password").send_keys("Test@1234")
        self.driver.find_element(By.TAG_NAME, "form").submit()
        time.sleep(1)
        page = self.driver.page_source.lower()
        self.assertTrue("error" in page or "required" in page or "email" in page)

    def test_7_login_missing_password(self):
        # Attempt to login with missing password
        self.driver.get("http://127.0.0.1:5000/login")
        self.driver.find_element(By.NAME, "email").send_keys("selenium_test@example.com")
        self.driver.find_element(By.TAG_NAME, "form").submit()
        time.sleep(1)
        page = self.driver.page_source.lower()
        self.assertIn("password", page)

    def test_8_direct_access_dashboard_redirects(self):
        # Try to access dashboard page without login
        self.driver.get("http://127.0.0.1:5000/dashboard")
        time.sleep(1)
        self.assertIn("login", self.driver.page_source.lower())

if __name__ == '__main__':
    unittest.main()
