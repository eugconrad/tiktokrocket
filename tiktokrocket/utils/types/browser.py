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
    headless: bool
    proxy: dict | None
    user_agent: str
    options: uc.ChromeOptions
    sw_options: dict
    driver: uc

    def __init__(self):
        pass

    def create(self, browser_path: str, headless: bool = False, proxy: str = None, user_agent: str = None):
        # --- Browser path ---
        driver_executable_path = os.path.join(browser_path, 'chromedriver.exe')
        browser_executable_path = os.path.join(browser_path, 'chrome.exe')

        # --- Headless ---
        self.headless = headless

        # --- Proxy ---
        self.proxy = None
        if proxy:
            self.proxy = {"server": f"http://{proxy}"}
            if "@" in proxy:
                self.proxy["server"] = f"http://{proxy.split('@')[1]}"
                self.proxy["username"] = proxy.split("@")[0].split(":")[0]
                self.proxy["password"] = proxy.split("@")[0].split(":")[1]

        # --- User agent ---
        if user_agent:
            self.user_agent = user_agent
        else:
            ua = UserAgent(browsers=["chrome"], os=["windows"], platforms=["pc"])
            self.user_agent = ua.random
        if self.user_agent.endswith(" "):
            self.user_agent = self.user_agent[:-1]

        # --- Chrome options ---
        self.options = uc.ChromeOptions()
        self.options.add_argument(f"--user-agent={user_agent}")

        # Set Chrome options for better automation experience
        self.options.add_argument("--disable-popup-blocking")  # Disable any popups that may interrupt
        self.options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.popups": 1,
            "profile.default_content_setting_values.notifications": 1,
            # "profile.managed_default_content_settings.images": 2,
            # "profile.managed_default_content_settings.css": 2,
        })

        # Additional Chrome self.options to optimize performance and stability
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
        self.options.add_argument("--disable-infobars")  # Disable annoying info bars in Chrome
        self.options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection as a bot
        self.options.add_argument("--no-sandbox")  # Fix issues in some environments
        self.options.add_argument("--disable-dev-shm-usage")  # Handle resource issues
        self.options.add_argument("--disable-gpu")  # Disable GPU acceleration

        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--disable-extensions")

        # --- Selenium wire options ---
        self.sw_options = dict()
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

    def reset(self):
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")

    def quit(self):
        self.driver.quit()
