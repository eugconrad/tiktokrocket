#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: browser.py
Date: 05.02.2025
License: Non-Commercial License

Author: me@eugconrad.com
Social: @eugconrad – Telegram, Lolzteam

      https://eugconrad.com
        © Copyright 2024
"""
import os
from fake_useragent import UserAgent
from seleniumwire import undetected_chromedriver as uc
from selenium_stealth import stealth


class Browser:
    """
    Class for managing browser interactions using Selenium and undetected_chromedriver.
    """

    headless: bool
    proxy: dict | None
    user_agent: str
    options: uc.ChromeOptions
    sw_options: dict
    driver: uc

    def create(
            self,
            browser_path: str,
            headless: bool = False,
            proxy: str = None,
            user_agent: str = None
    ):
        """
        Creates and configures a new browser instance with specified settings.

        Args:
            browser_path (str): Path to the browser executable and driver.
            headless (bool): Whether to run the browser in headless mode.
            proxy (str, optional): Proxy server address with optional authentication.
            user_agent (str, optional): Custom user agent string.
        """
        # --- Browser path ---
        driver_executable_path = os.path.join(browser_path, 'chromedriver.exe')
        browser_executable_path = os.path.join(browser_path, 'chrome.exe')

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

        # --- Selenium wire options ---
        self.sw_options = {}
        self.sw_options['verify_ssl'] = False
        if self.proxy:
            self.sw_options['proxy'] = self.proxy

        # --- Browser ---
        self.driver = uc.Chrome(
            options=self.options,
            seleniumwire_options=self.sw_options,
            driver_executable_path=driver_executable_path,
            browser_executable_path=browser_executable_path,
            version_main=127,
            headless=self.headless
        )
        self.driver.implicitly_wait(0.5)
        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        self.driver.maximize_window()
        self.driver.implicitly_wait(0.5)

    @staticmethod
    def _get_proxy(proxy):
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
        if user_agent:
            return user_agent.rstrip()
        return UserAgent(browsers=["chrome"], os=["windows"], platforms=["pc"]).random

    def reset(self):
        """
        Resets the browser session by clearing cookies and storage.
        """
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")

    def add_cookies(self, cookies: list):
        """
        Adds many cookies from the list to the current session.
        """
        for cookie in cookies:
            if not isinstance(cookie, dict):
                continue
            self.driver.add_cookie(cookie)

    def quit(self):
        """
        Quits the browser session and closes the browser window.
        """
        self.driver.quit()
