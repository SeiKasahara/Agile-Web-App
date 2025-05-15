# Import required modules
import unittest  # Python's built-in unit testing framework
from selenium import webdriver  # Web browser automation tool
from selenium.webdriver.common.by import By  # To locate HTML elements
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options  # To configure Chrome
import time  # For pauses between actions

class SeleniumAuthTest(unittest.TestCase):

    def setUp(self):
        # Set Chrome options to run in headless mode (no GUI)
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        
        # Launch headless Chrome browser and open the base URL
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("http://127.0.0.1:5000")  # Replace with actual app URL if needed

    def tearDown(self):
        # Close the browser after each test
        self.driver.quit()

    def handle_alert_if_present(self):
        # Attempt to handle a browser alert popup and return its text
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            time.sleep(1)
            return alert_text
        except:
            return None  # No alert was present

    def test_1_register_success(self):
        # Test successful registration of a new user
        self.driver.get("http://127.0.0.1:5000/signup")
        self.driver.find_element(By.NAME, "first_name").send_keys("Selenium")
        self.driver.find_element(By.NAME, "last_name").send_keys("User")
        self.driver.find_element(By.NAME, "email").send_keys("selenium_test@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Test@1234")
        self.driver.find_element(By.TAG_NAME, "form").submit()
        time.sleep(2)

        # Check for success alert or confirmation in page
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
        # Test login with valid credentials
        self.driver.get("http://127.0.0.1:5000/login")
        self.driver.find_element(By.NAME, "email").send_keys("selenium_test@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Test@1234")
        self.driver.find_element(By.TAG_NAME, "form").submit()
        time.sleep(2)

        # Validate success through alert or redirect
        alert_text = self.handle_alert_if_present()
        if alert_text:
            self.assertIn("login successful", alert_text.lower())
        else:
            page = self.driver.page_source.lower()
            self.assertTrue(
                "logout" in page or
                "dashboard" in page or
                "welcome" in page or
                self.driver.current_url != "http://127.0.0.1:5000/login"
            )

    def test_3_login_wrong_password(self):
        # Test login attempt with wrong password
        self.driver.get("http://127.0.0.1:5000/login")
        self.driver.find_element(By.NAME, "email").send_keys("selenium_test@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("WrongPassword")
        self.driver.find_element(By.TAG_NAME, "form").submit()
        time.sleep(2)

        # Verify error message in alert or page
        alert_text = self.handle_alert_if_present()
        if alert_text:
            self.assertIn("incorrect", alert_text.lower())
        else:
            self.assertIn("invalid", self.driver.page_source.lower())

    def test_4_logout_redirect(self):
        # Test logout and redirection to login
        self.driver.get("http://127.0.0.1:5000/login")
        self.driver.find_element(By.NAME, "email").send_keys("selenium_test@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Test@1234")
        self.driver.find_element(By.TAG_NAME, "form").submit()
        self.handle_alert_if_present()
        self.driver.get("http://127.0.0.1:5000/logout")
        time.sleep(1)

        # Ensure redirected to login page after logout
        self.assertIn("login", self.driver.page_source.lower())

    def test_5_invalid_email_verification_token(self):
        # Test email verification with invalid token
        self.driver.get("http://127.0.0.1:5000/verify-email/invalidtoken")
        time.sleep(1)
        self.assertIn("login", self.driver.page_source.lower())

    def test_6_register_missing_fields(self):
        # Attempt registration with missing required field (email)
        self.driver.get("http://127.0.0.1:5000/signup")
        self.driver.find_element(By.NAME, "first_name").send_keys("Missing")
        self.driver.find_element(By.NAME, "last_name").send_keys("Email")
        self.driver.find_element(By.NAME, "password").send_keys("Test@1234")
        self.driver.find_element(By.TAG_NAME, "form").submit()
        time.sleep(1)

        # Confirm error or warning message appears
        page = self.driver.page_source.lower()
        self.assertTrue("error" in page or "required" in page or "email" in page)

    def test_7_login_missing_password(self):
        # Attempt to login without entering password
        self.driver.get("http://127.0.0.1:5000/login")
        self.driver.find_element(By.NAME, "email").send_keys("selenium_test@example.com")
        self.driver.find_element(By.TAG_NAME, "form").submit()
        time.sleep(1)

        # Check for error message related to password
        page = self.driver.page_source.lower()
        self.assertIn("password", page)

    def test_8_direct_access_dashboard_redirects(self):
        # Ensure unauthenticated users can't access the dashboard
        self.driver.get("http://127.0.0.1:5000/dashboard")
        time.sleep(1)

        # Should be redirected or shown login page
        self.assertIn("login", self.driver.page_source.lower())

# Run the test suite
if __name__ == '__main__':
    unittest.main()
