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
import gzip
import re

import brotli
import zstandard
from io import BytesIO
from pathlib import Path
from typing import List, Optional

import ua_generator
from ua_generator.user_agent import UserAgent
from seleniumwire import undetected_chromedriver as uc
from seleniumwire.request import Request, Response
from selenium_stealth import stealth
from loguru import logger


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
        open(url, in_new_tab): Opens the specified URL in the browser.
        reset(): Resets the browser session by clearing cookies and storage.
        add_cookies(cookies): Adds cookies to the current browser session.
        get_cookies(): Retrieves all cookies from the current browser session.
        quit(): Closes the browser and terminates the WebDriver session.
    """
    browser_executable_file: Path
    driver_executable_file: Path
    user_data_dir: Path
    headless: bool
    proxy: Optional[dict[str, str]]
    user_agent: UserAgent
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

    def create(
            self,
            headless: bool = False,
            proxy: Optional[str] = None
    ) -> None:
        """
        Creates and configures a new browser instance with specified settings.

        Args:
            headless (bool): Whether to run the browser in headless mode.
            proxy (Optional[str]): Proxy server address with optional authentication.

        Returns:
            None
        """
        # --- Headless ---
        self.headless = headless

        # --- Proxy ---
        self.proxy = self._get_proxy(proxy=proxy)

        # --- User agent ---
        self.user_agent = self._generate_user_agent()

        # --- Chrome options ---
        options = self._get_chrome_options(user_agent=self.user_agent)

        # --- Selenium wire options ---
        sw_options = {
            'verify_ssl': False,
            'suppress_connection_errors': False,
            'request_storage': 'memory',
            'request_storage_max_size': 100,
        }

        if self.proxy:
            sw_options['proxy'] = self.proxy

        # --- Browser ---
        self.driver = uc.Chrome(
            options=options,
            driver_executable_path=self.driver_executable_file.absolute().as_posix(),
            browser_executable_path=self.browser_executable_file.absolute().as_posix(),
            headless=self.headless,
            seleniumwire_options=sw_options
        )

        # --- Request interceptor ---
        self.driver.request_interceptor = self._request_interceptor
        self.driver.response_interceptor = self._response_interceptor

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

    def _request_interceptor(self, request: Request):
        match = re.search(r'"Google Chrome";v="(\d+)', self.user_agent.ch.brands)
        if match:
            major_version = int(match.group(1))
        else:
            major_version = "127"

        if "User-Agent" in request.headers:
            del request.headers['User-Agent']
        request.headers['User-Agent'] = self.user_agent.text

        if "Dnt" in request.headers:
            del request.headers["Dnt"]

        if "Sec-Ch-Ua" in request.headers:
            del request.headers["Sec-Ch-Ua"]
        request.headers["Sec-Ch-Ua"] = f'"Chromium";v="{major_version}", "Not)A;Brand";v="99"'

        if "Sec-Ch-Ua-Mobile" in request.headers:
            del request.headers["Sec-Ch-Ua-Mobile"]
        request.headers["Sec-Ch-Ua-Mobile"] = self.user_agent.ch.mobile

        if "Sec-Ch-Ua-Platform" in request.headers:
            del request.headers["Sec-Ch-Ua-Platform"]
        request.headers["Sec-Ch-Ua-Platform"] = self.user_agent.ch.platform

    def _response_interceptor(self, request: Request, response: Response):
        if 'tiktok.com/passport' in request.url:
            logger.debug(request)
            logger.debug(self._decompress_response(response))

    @staticmethod
    def _decompress_response(response: Response) -> str:
        encoding = response.headers.get('Content-Encoding', '').lower()
        body = response.body

        try:
            if encoding == 'gzip':
                return gzip.GzipFile(fileobj=BytesIO(body)).read().decode('utf-8')
            elif encoding == 'br':
                return brotli.decompress(body).decode('utf-8')
            elif encoding == 'zstd':
                dctx = zstandard.ZstdDecompressor()
                return dctx.decompress(body).decode('utf-8')
            else:
                return body.decode('utf-8')
        except Exception as e:
            return f"[Ошибка декодирования: {e}]"

    @staticmethod
    def _get_proxy(proxy: Optional[str]) -> Optional[dict[str, str]]:
        """
        Преобразует прокси строку в формат selenium-wire.

        Поддерживает:
        - 'ip:port'
        - 'user:pass@ip:port'
        - 'http://ip:port'
        - 'http://user:pass@ip:port'
        - 'socks5://ip:port'
        - 'socks5://user:pass@ip:port'

        Возвращает:
            dict | None: Словарь формата:
            {
                'http': 'scheme://user:pass@ip:port',
                'https': 'scheme://user:pass@ip:port',
                'no_proxy': 'localhost,127.0.0.1'
            }
        """
        if not proxy:
            return None

        # Если нет схемы, по умолчанию http
        if "://" not in proxy:
            proxy = f"http://{proxy}"

        # selenium-wire требует один и тот же прокси для http и https
        return {
            "http": proxy,
            "https": proxy,
            "no_proxy": "localhost,127.0.0.1"
        }

    @staticmethod
    def _generate_user_agent() -> UserAgent:
        """
        Generate or return a user agent object.
        """
        user_agent = ua_generator.generate(
            device='desktop',
            platform='windows',
            browser='chrome'
        )
        return user_agent

    @staticmethod
    def _get_chrome_options(user_agent: UserAgent) -> uc.ChromeOptions:
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
        options.add_argument(f"--user-agent={user_agent.text}")

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

    def open(self, url: str, in_new_tab: bool = False) -> None:
        """
        Opens the specified URL in the browser and returns the Browser instance.
        If in_new_tab=True, opens in a new tab and closes the current one.

        Args:
            url: URL to open
            in_new_tab: If True, will replace current tab with new one
        """
        if in_new_tab:
            current_tab_handle = self.driver.current_window_handle
            self.driver.switch_to.new_window('tab')
            new_tab_handle = self.driver.current_window_handle
            self.driver.switch_to.window(current_tab_handle)
            self.driver.close()
            self.driver.switch_to.window(new_tab_handle)
        self.driver.get(url=url)

    def reset(self) -> None:
        """
        Fully resets the browser session with multiple cleanup options.
        """
        # Clear all browser data
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")

        # Clear IndexedDB if needed
        self.driver.execute_script("""
            try {
                indexedDB.databases().then(dbs => {
                    for (let db of dbs) {
                        indexedDB.deleteDatabase(db.name);
                    }
                });
            } catch(e) {}
        """)

        # Clear service workers
        self.driver.execute_script("""
            navigator.serviceWorker.getRegistrations().then(registrations => {
                for (let registration of registrations) {
                    registration.unregister();
                }
            });
        """)

        # Save current tab if we need to close others
        current_tab = self.driver.current_window_handle

        # Close all extra tabs
        for handle in self.driver.window_handles:
            if handle != current_tab:
                self.driver.switch_to.window(handle)
                self.driver.close()
        self.driver.switch_to.window(current_tab)

        self.open(url="about:blank", in_new_tab=True)

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
