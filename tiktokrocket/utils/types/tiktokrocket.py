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
    Класс TikTokRocket управляет инициализацией и процессом аутентификации
    для приложения TikTokRocket. Настраивает необходимые директории,
    проверяет операционную систему, загружает переменные окружения
    и обрабатывает аутентификацию пользователя через GUI Tkinter.
    """

    def __init__(self):
        """
        Инициализирует экземпляр TikTokRocket, настраивая директории,
        проверяя ОС, загружая переменные окружения и проверяя аутентификацию.
        """
        # Создаем окно загрузки
        loading_window = UiWindow(title="TikTokRocket", geometry="300x60")
        loading_window_label = ttk.Label(loading_window.root, text="Инициализация...")
        loading_window_label.pack(pady=10)

        loading_window_progress = ttk.Progressbar(loading_window.root, mode='indeterminate')
        loading_window_progress.pack(fill=tk.X, padx=20)
        loading_window_progress.start()
        loading_window.root.update()

        self._app_name = "TikTokRocket-core"
        self._system_name = platform.system()

        loading_window_label.config(text="Проверка совместимости...")
        loading_window.root.update()

        try:
            self._validate_os()
            logger.debug("Проверка совместимости выполнена успешно")
        except RuntimeError as err:
            logger.error(f"Ошибка Проверки совместимости: {err}")
            raise

        self.data_dir = Path(user_data_dir(self._app_name))
        logger.debug(f"Директория данных: {self.data_dir}")

        loading_window_label.config(text="Создание рабочих директорий...")
        loading_window.root.update()

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
        loading_window.root.update()

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
        loading_window.root.update()

        try:
            self.env = Env(env_file=self.env_file)
            logger.info("Конфигурация окружения загружена")
        except Exception as err:
            logger.error(f"Ошибка загрузки конфигурации: {err}")
            raise

        # Инициализация клиента
        loading_window_label.config(text="Инициализация клиента...")
        loading_window.root.update()

        access_token = self.env.get("access_token")
        logger.debug(f"Токен доступа: {'есть' if access_token else 'отсутствует'}")
        self.client = Client(access_token)

        # Проверка аутентификации
        loading_window_label.config(text="Проверка аутентификации...")
        loading_window.root.update()

        if not self._check_auth():
            logger.warning("Пользователь не аутентифицирован, запуск процесса входа")
            self._run_login_window()
        else:
            logger.info("Пользователь успешно аутентифицирован")

        # Инициализация и установка браузера
        loading_window_label.config(text="Инициализация браузера...")
        loading_window.root.update()

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
            loading_window.root.update()

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
        loading_window.close()

    def _validate_os(self) -> None:
        """
        Проверяет совместимость операционной системы с TikTokRocket.

        Raises:
            RuntimeError: Если ОС не Windows или Linux
        """
        logger.debug(f"Проверка ОС: {platform.system()}")

        if self._system_name.lower() not in ["windows", "linux", "darwin"]:
            error_msg = f"{self._app_name} поддерживается только на Windows, Linux, MacOS"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _check_auth(self) -> bool:
        """
        Проверяет аутентификацию пользователя через получение данных пользователя.

        Returns:
            bool: True если данные получены успешно, иначе False
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

        login_window = UiWindow(title=self._app_name, geometry="300x220")
        tk.Label(login_window.root, text="Вход", font=("Arial", 18, "bold")).pack(pady=10)

        # Поле ввода имени пользователя
        tk.Label(login_window.root, text="Логин", font=("Arial", 12)).pack(anchor="w", padx=30)
        login_entry = tk.Entry(login_window.root, font=("Arial", 12))
        login_entry.pack(fill="x", padx=30, pady=(0, 10))

        # Поле ввода пароля
        tk.Label(login_window.root, text="Пароль", font=("Arial", 12)).pack(anchor="w", padx=30)
        password_entry = tk.Entry(login_window.root, font=("Arial", 12), show="*")
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
                    # Сохраняем токен в .env файл
                    self.env.set(key="access_token", value=access_token)
                    logger.debug("Токен доступа сохранен в конфигурации")
                    messagebox.showinfo("Успех", "Авторизация прошла успешно!")
                    login_window.close()
                else:
                    logger.warning("Неудачная попытка входа")
                    messagebox.showerror("Ошибка", "Войти не удалось!")
            except Exception as err:
                logger.error(f"Ошибка аутентификации: {str(err)}")
                messagebox.showerror("Ошибка", f"Ошибка авторизации: {str(err)}")

        # Кнопка входа
        login_button = tk.Button(login_window.root, text="Войти", font=("Arial", 12), command=_login)
        login_button.pack(padx=30, fill="x")

        logger.debug("Отображение окна аутентификации")
        login_window.root.mainloop()
        login_window.root.update()
        logger.info("Процесс аутентификации завершен")
