#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: updater.py
Date: 25.02.2025
License: Non-Commercial License

Author: me@eugconrad.com
Social: @eugconrad – Telegram, Lolzteam

      https://eugconrad.com
        © Copyright 2024
"""
import os
import sys
import zipfile
from pathlib import Path

import requests

from tiktokrocket.data import Config


class Updater:
    """
    The Updater class manages the installation and updating of the Chrome browser
    and its driver for the TikTokRocket application. It ensures compatibility with
    Windows platforms, handles the creation of necessary directories, and provides
    methods to check the installation status, clear existing installations, and
    download and install the latest browser version using an access token for
    authorization.

    Attributes:
        storage_dir (Path): The directory path for storing browser-related files.
        browser_path (Path): The path to the directory containing the browser and driver.
        driver_executable_path (Path): The path to the Chrome driver executable.
        browser_executable_path (Path): The path to the Chrome browser executable.
    """

    def __init__(self):
        """
        Initializes the Updater instance, setting up necessary paths for
        browser and driver executables. Ensures the application is running
        on a Windows platform and creates the required storage directory.

        Raises:
            RuntimeError: If the platform is not Windows.
        """
        if sys.platform != "win32":
            raise RuntimeError("TikTokRocket поддерживается только на Windows")

        self.storage_dir = Path(os.getenv("APPDATA")) / ".tiktokrocket"
        self.browser_path = self.storage_dir / "selenium-browser"
        self.driver_executable_path = self.browser_path / "chromedriver.exe"
        self.browser_executable_path = self.browser_path / "chrome.exe"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    @property
    def is_browser_installed(self):
        """
        Checks if both the browser and driver executables are installed.

        Returns:
            bool: True if both executables exist, False otherwise.
        """
        if self.driver_executable_path.exists() and self.browser_executable_path.exists():
            return True
        return False

    def _clear_browser_directory(self):
        """
        Removes all files and directories within the browser path directory.
        If the directory does not exist, no action is taken.
        """
        if self.browser_path.exists():
            for item in self.browser_path.iterdir():
                if item.is_file():
                    item.unlink()
                else:
                    os.rmdir(item)

    def _download_browser(self, access_token: str):
        """
        Downloads the latest version of the Chrome browser as a zip file.

        Args:
            access_token (str): The access token for authorization.

        Raises:
            HTTPError: If the HTTP request for downloading the browser fails.
        """
        config = Config()

        url = config.get_api_endpoint("download_chrome")
        headers = {"Authorization": access_token, "Content-Type": "application/json; charset=utf-8"}
        timeout = config.get_timeout()

        response = requests.get(url=url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()

        filename = "chrome-latest.zip"
        filepath = self.storage_dir / filename
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    def install_browser(self, access_token: str, reinstall: bool = False):
        """
        Installs the Chrome browser by downloading and extracting the latest
        version. If the browser is already installed and `reinstall` is False,
        the installation is skipped.

        Args:
            access_token (str): The access token for authorization.
            reinstall (bool): If True, forces reinstallation even if the browser
                              is already installed. Defaults to False.
        """
        if not reinstall and self.is_browser_installed:
            return

        self._clear_browser_directory()

        self._download_browser(access_token=access_token)

        zip_file_path = self.storage_dir / "chrome-latest.zip"
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(self.browser_path)

        zip_file_path.unlink()
