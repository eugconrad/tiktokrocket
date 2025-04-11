"""
File: browser.py
Created: 11.04.2025

This source code constitutes confidential information and is the 
exclusive property of the Author. You are granted a non-exclusive, 
non-transferable license to use this code for personal, non-commercial 
purposes only.

STRICTLY PROHIBITED:
- Any form of reproduction, distribution, or modification for commercial purposes
- Selling, licensing, sublicensing or otherwise monetizing this code
- Removing or altering this proprietary notice

Violations will be prosecuted to the maximum extent permitted by law.
For commercial licensing inquiries, contact author.

Author: me@eugconrad.com
Contacts:
  • Telegram: @eugconrad

Website: https://eugconrad.com
Copyright © 2025 All Rights Reserved
"""
from pathlib import Path

from fake_useragent import UserAgent
from seleniumwire import undetected_chromedriver as uc
from selenium_stealth import stealth


class Browser:
    """
    A class to manage browser instances using undetected ChromeDriver with
    customizable settings such as headless mode, proxy, and user agent.

    Attributes:
        headless (bool): Indicates if the browser runs in headless mode.
        proxy (dict | None): Proxy server details.
        user_agent (str): User agent string for the browser.
        options (uc.ChromeOptions): Chrome options for the browser.
        sw_options (dict): Selenium Wire options for the browser.
        driver (uc): The Chrome WebDriver instance.
    """
    browser_executable_file: Path
    driver_executable_file: Path
    headless: bool
    proxy: dict | None
    user_agent: str
    options: uc.ChromeOptions
    sw_options: dict
    driver: uc

    def create(
            self,
            browser_executable_file: Path,
            driver_executable_file: Path,
            headless: bool = False,
            proxy: str = None,
            user_agent: str = None
    ):
        """
        Creates and configures a new browser instance with specified settings.

        Args:
            browser_executable_file (Path): Path to the browser executable.
            driver_executable_file (Path): Path to the browser driver.
            headless (bool): Whether to run the browser in headless mode.
            proxy (str, optional): Proxy server address with optional authentication.
            user_agent (str, optional): Custom user agent string.
        """
        # --- Browser path ---
        self.browser_executable_file = browser_executable_file
        self.driver_executable_file = driver_executable_file

        # --- Headless ---
        self.headless = headless

        # --- Proxy ---
        self.proxy = self._get_proxy(proxy)

        # --- User agent ---
        self.user_agent = self._get_user_agent(user_agent)

        # --- Chrome options ---
        self.options = uc.ChromeOptions()
        self.options.add_argument(f"--user-agent={self.user_agent}")

        # Set Chrome options for better automation experience
        self.options.add_argument("--disable-popup-blocking")
        self.options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.popups": 1,
            "profile.default_content_setting_values.notifications": 1,
        })

        # Additional Chrome options to optimize performance and stability
        self.options.add_argument("--disable-background-networking")
        self.options.add_argument("--disable-background-timer-throttling")
        self.options.add_argument("--disable-backgrounding-occluded-windows")
        self.options.add_argument("--disable-breakpad")
        self.options.add_argument("--disable-client-side-phishing-detection")
        self.options.add_argument("--disable-default-apps")
        self.options.add_argument("--disable-hang-monitor")
        self.options.add_argument("--disable-prompt-on-repost")
        self.options.add_argument("--disable-sync")
        self.options.add_argument("--metrics-recording-only")
        self.options.add_argument("--no-first-run")
        self.options.add_argument("--safebrowsing-disable-auto-update")
        self.options.add_argument("--password-store=basic")
        self.options.add_argument("--use-mock-keychain")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")

        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--disable-extensions")

        self.options.page_load_strategy = 'eager'

        # --- Selenium wire options ---
        self.sw_options = {}
        self.sw_options['verify_ssl'] = False
        if self.proxy:
            self.sw_options['proxy'] = self.proxy

        # --- Browser ---
        self.driver = uc.Chrome(
            options=self.options,
            seleniumwire_options=self.sw_options,
            driver_executable_path=self.driver_executable_file.absolute().as_posix(),
            browser_executable_path=self.browser_executable_file.absolute().as_posix(),
            version_main=127,
            headless=self.headless
        )
        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    @staticmethod
    def _get_proxy(proxy):
        """
        Parses a proxy string and returns a dictionary with proxy server details.

        Args:
            proxy (str): Proxy server address with optional authentication in the
                         format 'username:password@server' or 'server'.

        Returns:
            dict | None: A dictionary containing the proxy server details with keys
                         'server', 'username', and 'password', or None if no proxy
                         is provided.
        """
        if proxy:
            proxy_parts = proxy.split("@")
            proxy_data = {"server": f"http://{proxy_parts[-1]}"}
            if len(proxy_parts) > 1:
                username, password = proxy_parts[0].split(":")
                proxy_data.update({"username": username, "password": password})
            return proxy_data
        return None

    @staticmethod
    def _get_user_agent(user_agent):
        """
        Returns a user agent string. If a user agent is provided, it returns
        the trimmed version of it. Otherwise, it generates a random user agent
        for Chrome on Windows PC using the UserAgent library.

        Args:
            user_agent (str): Custom user agent string.

        Returns:
            str: A user agent string.
        """
        if user_agent:
            return user_agent.rstrip()
        return UserAgent(browsers=["chrome"], os=["windows"], platforms=["pc"]).random

    def open(self, url: str):
        """
        Opens the specified URL in the browser and returns the Browser instance.

        Args:
            url (str): The URL to be opened in the browser.

        Returns:
            Browser: The current instance of the Browser class.
        """
        self.driver.get(url=url)
        return self

    def reset(self):
        """
        Resets the browser session by clearing all cookies, local storage, and session storage.
        """
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")

    def add_cookies(self, cookies: list):
        """
        Adds a list of cookies to the current browser session.

        Args:
            cookies (list): A list of cookies, where each cookie is represented as a dictionary.
        """
        for cookie in cookies:
            if not isinstance(cookie, dict):
                continue
            self.driver.add_cookie(cookie)

    def quit(self):
        """
        Closes the browser and terminates the WebDriver session.
        """
        self.driver.quit()
