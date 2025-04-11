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


class LoadingWindow:
    """Окно для отображения процесса загрузки"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TikTokRocket - Загрузка")
        self.root.geometry("300x100")
        self.root.resizable(False, False)

        # Центрирование окна
        self._center_window()

        self.label = ttk.Label(self.root, text="Инициализация приложения...")
        self.label.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20)
        self.progress.start()

    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def update_text(self, text):
        """Обновляет текст загрузки"""
        self.label.config(text=text)
        self.root.update()

    def close(self):
        """Закрывает окно загрузки"""
        self.root.destroy()


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
        self.loading_window = LoadingWindow()
        self.loading_window.update_text("Инициализация TikTokRocket...")

        logger.info("Инициализация TikTokRocket")
        self._app_name = "TikTokRocket-core"
        self._system_name = platform.system()

        try:
            self.loading_window.update_text("Проверка операционной системы...")
            self._validate_os()
            logger.debug("Проверка ОС выполнена успешно")
        except RuntimeError as e:
            logger.error(f"Ошибка проверки ОС: {e}")
            self.loading_window.update_text(f"Ошибка: {e}")
            raise

        self.data_dir = Path(user_data_dir(self._app_name))
        logger.debug(f"Директория данных: {self.data_dir}")

        try:
            self.loading_window.update_text("Создание директорий...")
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Директория данных создана или уже существует")
        except Exception as e:
            logger.error(f"Ошибка создания директории данных: {e}")
            self.loading_window.update_text(f"Ошибка: {e}")
            raise

        self.browser_dir = self.data_dir / "selenium-browser"
        logger.debug(f"Директория браузера: {self.browser_dir}")

        try:
            self.browser_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Директория браузера создана или уже существует")
        except Exception as e:
            logger.error(f"Ошибка создания директории браузера: {e}")
            self.loading_window.update_text(f"Ошибка: {e}")
            raise

        # Определяем пути к исполняемым файлам
        self.loading_window.update_text("Настройка путей...")
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
            error = "Неподдерживаемая операционная система"
            self.loading_window.update_text(error)
            raise RuntimeError(error)

        logger.debug(f"Файл драйвера: {self.driver_executable_file}")
        logger.debug(f"Файл браузера: {self.browser_executable_file}")

        self.env_file = self.data_dir / "config.env"
        logger.debug(f"Файл конфигурации: {self.env_file}")

        try:
            self.loading_window.update_text("Загрузка конфигурации...")
            self.env = Env(env_file=self.env_file)
            logger.info("Конфигурация окружения загружена")
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            self.loading_window.update_text(f"Ошибка: {e}")
            raise

        # Инициализация клиента
        self.loading_window.update_text("Инициализация клиента...")
        access_token = self.env.get("access_token")
        logger.debug(f"Токен доступа: {'есть' if access_token else 'отсутствует'}")
        self.client = Client(access_token)

        # Проверка аутентификации
        self.loading_window.update_text("Проверка аутентификации...")
        if not self._check_auth():
            logger.warning("Пользователь не аутентифицирован, запуск процесса входа")
            self._run_login_flow()
        else:
            logger.info("Пользователь успешно аутентифицирован")

        # Инициализация и установка браузера
        self.loading_window.update_text("Инициализация браузера...")
        logger.info("Инициализация Updater")
        self.updater = Updater(
            data_dir=self.data_dir,
            browser_dir=self.browser_dir,
            driver_executable_file=self.driver_executable_file,
            browser_executable_file=self.browser_executable_file,
        )

        self.loading_window.update_text("Установка браузера...")
        logger.info("Запуск установки браузера")
        try:
            result = self.updater.install_browser()
            if result:
                logger.info("Браузер успешно установлен")
                self.loading_window.update_text("Готово!")
            else:
                error = "Ошибка установки браузера"
                self.loading_window.update_text(error)
                raise RuntimeError(error)
        except Exception as e:
            logger.error(f"Ошибка установки браузера: {e}")
            self.loading_window.update_text(f"Ошибка: {e}")
            raise

        # Закрываем окно загрузки после успешной инициализации
        self.loading_window.close()

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

    def _run_login_flow(self) -> None:
        """
        Запускает процесс входа через GUI Tkinter.

        Создает окно для ввода учетных данных, сохраняет токен доступа
        при успешной аутентификации и отображает сообщения об ошибках.
        """
        logger.info("Запуск процесса аутентификации через GUI")

        root = tk.Tk()
        root.title(self._app_name)
        root.geometry("300x220")
        root.resizable(False, False)

        # Заголовок
        tk.Label(root, text="Вход", font=("Arial", 18, "bold")).pack(pady=10)

        # Поле ввода имени пользователя
        tk.Label(root, text="Логин", font=("Arial", 12)).pack(anchor="w", padx=30)
        login_entry = tk.Entry(root, font=("Arial", 12))
        login_entry.pack(fill="x", padx=30, pady=(0, 10))

        # Поле ввода пароля
        tk.Label(root, text="Пароль", font=("Arial", 12)).pack(anchor="w", padx=30)
        password_entry = tk.Entry(root, font=("Arial", 12), show="*")
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
                    root.destroy()
                else:
                    logger.warning("Неудачная попытка входа")
                    messagebox.showerror("Ошибка", "Войти не удалось!")
            except Exception as err:
                logger.error(f"Ошибка аутентификации: {str(err)}")
                messagebox.showerror("Ошибка", f"Ошибка авторизации: {str(err)}")

        # Кнопка входа
        login_button = tk.Button(root, text="Войти", font=("Arial", 12), command=_login)
        login_button.pack(padx=30, fill="x")

        logger.debug("Отображение окна аутентификации")
        root.mainloop()
        logger.info("Процесс аутентификации завершен")
