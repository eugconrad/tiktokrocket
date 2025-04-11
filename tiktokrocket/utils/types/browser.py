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
from typing import List, Optional

from fake_useragent import UserAgent
from seleniumwire import undetected_chromedriver as uc
from selenium_stealth import stealth


class Browser:
    """
    A class to manage browser instances using undetected ChromeDriver with
    customizable settings such as headless mode, proxy, and user agent.

    Attributes:
        browser_executable_file (Path): Path to the browser executable file.
        driver_executable_file (Path): Path to the driver executable file.
        user_data_dir (Path): Directory for user data.
        headless (bool): Indicates if the browser runs in headless mode.
        proxy (Optional[dict]): Proxy server details.
        user_agent (str): User agent string for the browser.
        driver (uc.Chrome): Chrome WebDriver instance.

    Methods:
        __init__(browser_executable_file, driver_executable_file): Initializes a Browser instance.
        create(headless, proxy, user_agent): Creates and configures a new browser instance.
        _get_proxy(proxy): Parses a proxy string and returns proxy details.
        _get_user_agent(user_agent): Generates or returns a user agent string.
        _get_chrome_options(user_agent): Configures and returns ChromeOptions.
        open(url): Opens the specified URL in the browser.
        reset(): Resets the browser session by clearing cookies and storage.
        add_cookies(cookies): Adds cookies to the current browser session.
        get_cookies(): Retrieves all cookies from the current browser session.
        quit(): Closes the browser and terminates the WebDriver session.
    """
    browser_executable_file: Path
    driver_executable_file: Path
    user_data_dir: Path
    headless: bool
    proxy: Optional[dict]
    user_agent: str
    driver: uc.Chrome

    def __init__(self, browser_executable_file: Path, driver_executable_file: Path) -> None:
        """
        Initializes a Browser instance with specified executable file paths.

        Args:
            browser_executable_file (Path): The path to the browser executable file.
            driver_executable_file (Path): The path to the driver executable file.
        """
        # --- Browser path ---
        self.browser_executable_file = browser_executable_file
        self.driver_executable_file = driver_executable_file
        self.user_data_dir = self.browser_executable_file.parent / "user_data_dir"

    def create(
            self,
            headless: bool = False,
            proxy: Optional[str] = None,
            user_agent: Optional[str] = None
    ) -> None:
        """
        Creates and configures a new browser instance with specified settings.

        Args:
            headless (bool): Whether to run the browser in headless mode.
            proxy (Optional[str]): Proxy server address with optional authentication.
            user_agent (Optional[str]): User agent string to be used.

        Returns:
            None
        """
        # --- Headless ---
        self.headless = headless

        # --- Proxy ---
        self.proxy = self._get_proxy(proxy=proxy)

        # --- User agent ---
        self.user_agent = self._get_user_agent(user_agent=user_agent)

        # --- Chrome options ---
        options = self._get_chrome_options(user_agent=user_agent)

        # --- Selenium wire options ---
        sw_options = {'verify_ssl': False}
        if self.proxy:
            sw_options['proxy'] = self.proxy

        # --- Browser ---
        self.driver = uc.Chrome(
            options=options,
            user_data_dir=self.user_data_dir.absolute().as_posix(),
            driver_executable_path=self.driver_executable_file.absolute().as_posix(),
            browser_executable_path=self.browser_executable_file.absolute().as_posix(),
            headless=self.headless,
            seleniumwire_options=sw_options
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

        if not self.headless:
            self.driver.maximize_window()

    @staticmethod
    def _get_proxy(proxy) -> Optional[dict[str, str]]:
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
    def _get_user_agent(user_agent: Optional[str]) -> str:
        """
        Generate or return a user agent string.

        Args:
            user_agent (Optional[str]): A user agent string to be used. If None, a random
                                        user agent for Chrome on Windows PC is generated.

        Returns:
            str: A trimmed user agent string if provided, otherwise a randomly generated one.
        """
        if user_agent:
            return user_agent.rstrip()
        return UserAgent(browsers=["chrome"], os=["windows"], platforms=["pc"]).random

    @staticmethod
    def _get_chrome_options(user_agent: str) -> uc.ChromeOptions:
        """
        Configures and returns ChromeOptions for the undetected ChromeDriver.

        Args:
            user_agent (str): The user agent string to be used by the browser.

        Returns:
            uc.ChromeOptions: Configured ChromeOptions object with various
            settings to enhance automation performance and stability.
        """
        # --- Chrome options ---
        options = uc.ChromeOptions()
        options.add_argument(f"--user-agent={user_agent}")

        # Set Chrome options for better automation experience
        options.add_argument("--disable-popup-blocking")
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.popups": 1,
            "profile.default_content_setting_values.notifications": 1,
        })

        # Additional Chrome options to optimize performance and stability
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--disable-sync")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--no-first-run")
        options.add_argument("--safebrowsing-disable-auto-update")
        options.add_argument("--password-store=basic")
        options.add_argument("--use-mock-keychain")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-extensions")

        return options

    def open(self, url: str) -> None:
        """
        Opens the specified URL in the browser and returns the Browser instance.

        Args:
            url (str): The URL to be opened in the browser.
        """
        self.driver.get(url=url)

    def reset(self) -> None:
        """
        Resets the browser session by clearing all cookies, local storage,
        and session storage.
        """
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")

    def add_cookies(self, cookies: List[dict]) -> None:
        """
        Adds a list of cookies to the current browser session.

        Args:
            cookies (list): A list of cookies, where each cookie is represented as a dictionary.
        """
        if not cookies:
            return
        for cookie in cookies:
            if not isinstance(cookie, dict):
                continue
            self.driver.add_cookie(cookie)

    def get_cookies(self) -> List[dict]:
        """
        Retrieves all cookies from the current browser session.

        Returns:
            List[dict]: A list of cookies, where each cookie is represented as a dictionary.
        """
        cookies = self.driver.get_cookies()
        return cookies

    def quit(self) -> None:
        """
        Closes the browser and terminates the WebDriver session.
        """
        if self.driver:
            self.driver.quit()
