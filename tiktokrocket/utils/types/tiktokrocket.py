"""
File: tiktokrocket.py
Created: 09.04.2025

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
import platform
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from platformdirs import user_data_dir

from loguru import logger

from tiktokrocket.utils.types.env import Env
from tiktokrocket.utils.types.client import Client
from tiktokrocket.utils.types.updater import Updater
from tiktokrocket.utils.types.ui_window import UiWindow


class TikTokRocket:
    """
    The TikTokRocket class initializes and manages the TikTokRocket application,
    setting up directories, loading environment configurations, and handling
    authentication and browser installation.

    Attributes:
        loading_window (UiWindow): The loading window displayed during initialization.
        _app_name (str): The name of the application.
        _system_name (str): The name of the operating system.
        data_dir (Path): The directory for storing application data.
        browser_dir (Path): The directory for the browser installation.
        browser_executable_file (Path): The path to the browser executable.
        driver_executable_file (Path): The path to the browser driver executable.
        env_file (Path): The path to the environment configuration file.
        env (Env): The environment configuration manager.
        client (Client): The client for interacting with the TikTokRocket API.
        updater (Updater): The updater for managing browser installations.

    Methods:
        __init__(): Initializes the TikTokRocket instance, setting up directories,
            loading environment configurations, and checking authentication.
        _validate_os(): Validates the operating system compatibility.
        _check_auth(): Checks user authentication status.
        _run_login_window(): Executes the login flow using a GUI for user authentication.
    """

    def __init__(self) -> None:
        """
        Initializes the TikTokRocket instance, setting up the loading window,
        validating the operating system, creating necessary directories, and
        configuring paths for browser and driver executables. Loads environment
        configurations, initializes the client, checks user authentication, and
        manages browser installation using the Updater class.

        Raises:
            RuntimeError: If the operating system is unsupported or if browser
            installation fails.
        """
        # Создаем окно загрузки
        self.loading_window = UiWindow(title="TikTokRocket", geometry="300x100")
        loading_window_label = ttk.Label(self.loading_window.root, text="Инициализация...")
        loading_window_label.pack(pady=10)

        loading_window_progress = ttk.Progressbar(self.loading_window.root, mode='indeterminate')
        loading_window_progress.pack(fill=tk.X, padx=20)
        loading_window_progress.start()
        self.loading_window.root.update()

        self._app_name = "TikTokRocket-core"
        self._system_name = platform.system()

        loading_window_label.config(text="Проверка совместимости...")
        self.loading_window.root.update()

        try:
            self._validate_os()
            logger.debug("Проверка совместимости выполнена успешно")
        except RuntimeError as err:
            logger.error(f"Ошибка Проверки совместимости: {err}")
            raise

        self.data_dir = Path(user_data_dir(self._app_name))
        logger.debug(f"Директория данных: {self.data_dir}")

        loading_window_label.config(text="Создание рабочих директорий...")
        self.loading_window.root.update()

        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Директория данных создана или уже существует")
        except Exception as err:
            logger.error(f"Ошибка создания директории данных: {err}")
            raise

        self.browser_dir = self.data_dir / "selenium-browser"
        logger.debug(f"Директория браузера: {self.browser_dir}")

        try:
            self.browser_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Директория браузера создана или уже существует")
        except Exception as err:
            logger.error(f"Ошибка создания директории браузера: {err}")
            raise

        # Определяем пути к исполняемым файлам
        loading_window_label.config(text="Настройка путей...")
        self.loading_window.root.update()

        if self._system_name.lower() == "windows":
            self.browser_executable_file = self.browser_dir / "chrome.exe"
            self.driver_executable_file = self.browser_dir / "chromedriver.exe"

        elif self._system_name.lower() == "linux":
            self.browser_executable_file = self.browser_dir / "chrome"
            self.driver_executable_file = self.browser_dir / "chromedriver"

        elif self._system_name.lower() == "darwin":
            _ = "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
            self.browser_executable_file = self.browser_dir / _
            self.driver_executable_file = self.browser_dir / "chromedriver"

        else:
            err = "Неподдерживаемая операционная система"
            raise RuntimeError(err)

        logger.debug(f"Файл драйвера: {self.driver_executable_file}")
        logger.debug(f"Файл браузера: {self.browser_executable_file}")

        self.env_file = self.data_dir / "config.env"
        logger.debug(f"Файл конфигурации: {self.env_file}")

        loading_window_label.config(text="Загрузка конфигурации...")
        self.loading_window.root.update()

        try:
            self.env = Env(env_file=self.env_file)
            logger.info("Конфигурация окружения загружена")
        except Exception as err:
            logger.error(f"Ошибка загрузки конфигурации: {err}")
            raise

        # Инициализация клиента
        loading_window_label.config(text="Инициализация клиента...")
        self.loading_window.root.update()

        access_token = self.env.get("access_token")
        logger.debug(f"Токен доступа: {'есть' if access_token else 'отсутствует'}")
        self.client = Client(access_token)

        # Проверка аутентификации
        loading_window_label.config(text="Проверка аутентификации...")
        self.loading_window.root.update()

        if not self._check_auth():
            logger.warning("Пользователь не аутентифицирован, запуск процесса входа")
            self._run_login_window()
            self.loading_window.root.update()
        else:
            logger.info("Пользователь успешно аутентифицирован")

        # Инициализация и установка браузера
        loading_window_label.config(text="Инициализация браузера...")
        self.loading_window.root.update()

        logger.info("Инициализация Updater")
        self.updater = Updater(
            data_dir=self.data_dir,
            browser_dir=self.browser_dir,
            driver_executable_file=self.driver_executable_file,
            browser_executable_file=self.browser_executable_file,
        )

        is_browser_installed = self.updater.is_browser_installed()
        if not is_browser_installed:
            loading_window_label.config(text="Установка браузера (это займет время)...")
            self.loading_window.root.update()

            logger.info("Запуск установки браузера")
            try:
                result = self.updater.install_browser()
                if result:
                    logger.info("Браузер успешно установлен")
                else:
                    error = "Ошибка установки браузера"
                    raise RuntimeError(error)
            except Exception as err:
                logger.error(f"Ошибка установки браузера: {err}")
                raise

        # Закрываем окно загрузки после успешной инициализации
        self.loading_window.close()

    def _validate_os(self) -> None:
        """
        Validates the operating system compatibility for the TikTokRocket application.

        Logs the current operating system and checks if it is one of the supported
        systems: Windows, Linux, or MacOS. If the operating system is unsupported,
        logs an error message and raises a RuntimeError.

        Raises:
            RuntimeError: If the operating system is not supported.
        """
        logger.debug(f"Проверка ОС: {platform.system()}")

        if self._system_name.lower() not in ["windows", "linux", "darwin"]:
            error_msg = f"{self._app_name} поддерживается только на Windows, Linux, macOS"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _check_auth(self) -> bool:
        """
        Checks the user's authentication status by retrieving user data from the API.

        Logs the authentication process and returns a boolean indicating whether
        the user is authenticated.

        Returns:
            bool: True if the user is authenticated, False otherwise.
        """
        logger.debug("Проверка аутентификации пользователя")
        try:
            user_data = self.client.get_me()
            if not user_data:
                logger.warning("Данные пользователя не получены")
                return False

            logger.debug(f"Данные пользователя: {user_data}")
            logger.info("Аутентификация подтверждена")
            return True

        except Exception as e:
            logger.error(f"Ошибка при проверке аутентификации: {e}")
            return False

    def _run_login_window(self) -> None:
        """
        Executes the login flow using a GUI for user authentication.

        This method creates a login window with fields for username and password
        input. It handles user input validation and attempts to authenticate the
        user via the API. If successful, it saves the access token to the environment
        configuration and closes the login window. Displays appropriate messages
        for successful or failed login attempts.

        Raises:
            Exception: If an error occurs during the authentication process.
        """
        logger.info("Запуск процесса аутентификации через GUI")

        # Create login window as a Toplevel window
        login_window = tk.Toplevel()
        login_window.title(self._app_name)
        login_window.geometry("300x220")

        # Make the window modal
        login_window.grab_set()

        # Don't set it as transient to avoid the cycle
        # login_window.transient(self.loading_window.root)  # Remove this line

        tk.Label(login_window, text="Вход", font=("Arial", 18, "bold")).pack(pady=10)

        # Username field
        tk.Label(login_window, text="Логин", font=("Arial", 12)).pack(anchor="w", padx=30)
        login_entry = tk.Entry(login_window, font=("Arial", 12))
        login_entry.pack(fill="x", padx=30, pady=(0, 10))

        # Password field
        tk.Label(login_window, text="Пароль", font=("Arial", 12)).pack(anchor="w", padx=30)
        password_entry = tk.Entry(login_window, font=("Arial", 12), show="*")
        password_entry.pack(fill="x", padx=30, pady=(0, 15))

        def _login():
            login = login_entry.get()
            password = password_entry.get()

            if not login or not password:
                logger.warning("Попытка входа с пустыми полями")
                messagebox.showerror("Ошибка", "Введите логин и пароль")
                return

            logger.debug(f"Попытка входа для пользователя: {login}")

            try:
                access_token = self.client.login(login=login, password=password)

                if access_token:
                    logger.info("Успешная аутентификация")
                    self.env.set(key="access_token", value=access_token)
                    logger.debug("Токен доступа сохранен в конфигурации")
                    login_window.destroy()  # Use destroy instead of close
                else:
                    logger.warning("Неудачная попытка входа")
                    messagebox.showerror("Ошибка", "Войти не удалось!")
            except Exception as err:
                logger.error(f"Ошибка аутентификации: {str(err)}")
                messagebox.showerror("Ошибка", f"Ошибка авторизации: {str(err)}")

        # Login button
        login_button = tk.Button(login_window, text="Войти", font=("Arial", 12), command=_login)
        login_button.pack(padx=30, fill="x")

        logger.debug("Отображение окна аутентификации")
        login_window.wait_window()  # This will block until window is destroyed
        logger.info("Процесс аутентификации завершен")
