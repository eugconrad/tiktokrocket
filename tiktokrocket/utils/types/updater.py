"""
File: updater.py
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
import os
import stat
import shutil
import zipfile
import platform
from pathlib import Path
from typing import Optional

import requests
from loguru import logger

from tiktokrocket.data.config import ApiConfig


class Updater:
    """
    The Updater class manages the installation and maintenance of a browser and its driver.

    Methods:
        __init__: Initializes the Updater with directories and executable paths.
        _set_executable_permissions: Sets executable permissions for a file.
        _handle_macos_permissions: Removes quarantine attributes on macOS.
        _clear_browser_directory: Clears the browser directory of all contents.
        _download_browser: Downloads the browser package for the current OS.
        is_browser_installed: Checks if the browser and driver are installed and executable.
        install_browser: Installs or reinstalls the browser, handling all steps from download
        to permission setting.
    """

    def __init__(
            self,
            data_dir: Path,
            browser_dir: Path,
            driver_executable_file: Path,
            browser_executable_file: Path
    ) -> None:
        """
        Initializes an instance of the Updater class.

        Args:
            data_dir (Path): The directory for storing data.
            browser_dir (Path): The directory where the browser is installed.
            driver_executable_file (Path): The path to the browser driver executable.
            browser_executable_file (Path): The path to the browser executable.

        Sets:
            _system_name: The name of the operating system.
        """
        self.data_dir = data_dir
        self.temp_dir = self.data_dir / "temp"
        self.browser_dir = browser_dir
        self.driver_executable_file = driver_executable_file
        self.browser_executable_file = browser_executable_file
        self._system_name = platform.system()

    @staticmethod
    def _set_executable_permissions(file_path: Path) -> bool:
        """
        Sets executable permissions for the specified file.

        Args:
            file_path (Path): The path to the file for which to set executable permissions.

        Returns:
            bool: True if permissions were successfully set, False otherwise.

        Logs:
            Logs an error if the file does not exist or if there is an error
            setting permissions, including PermissionError, NotImplementedError,
            and OSError.
        """
        if not file_path.exists():
            logger.error(f"Файл не найден: {file_path}")
            return False

        try:
            current_mode = os.stat(file_path).st_mode
            os.chmod(file_path, current_mode | stat.S_IEXEC)
            logger.debug(f"Установлены права на исполнение для: {file_path}")
            return True

        except PermissionError as err:
            logger.error(f"Ошибка прав доступа: {err}")

        except NotImplementedError as err:
            logger.error(f"Функция не поддерживается: {err}")

        except OSError as err:
            logger.error(f"Ошибка ОС: {err}")

        return False

    def _handle_macos_permissions(self) -> None:
        """
        Removes the quarantine attribute from the browser and driver executables
        on macOS to bypass Gatekeeper restrictions.

        This method is only executed if the operating system is macOS (Darwin).
        Logs a debug message upon successful removal of the quarantine attributes.
        """
        if self._system_name.lower() != "darwin":
            return
        # Удаляем атрибут карантина (Gatekeeper)
        for path in [self.browser_executable_file, self.driver_executable_file]:
            os.system(f"xattr -d com.apple.quarantine \"{path.absolute().as_posix()}\"")
        logger.debug("Атрибуты карантина macOS удалены")

    def _clear_browser_directory(self) -> None:
        """
        Clears the browser directory by removing all files, directories, and symlinks.

        Logs:
            Logs the start and completion of the clearing process, including the number
            of items cleared. Logs errors if items cannot be removed due to permission
            issues or filesystem errors.
        """
        if not self.browser_dir.exists():
            logger.debug("Директория браузера не существует, очистка не требуется")
            return

        logger.info("Очистка директории браузера...")
        items_cleared = 0

        for item in self.browser_dir.iterdir():
            try:
                if item.is_symlink():
                    item.unlink()
                    logger.debug(f"Удален симлинк: {item}")
                elif item.is_file():
                    item.unlink(missing_ok=True)
                    logger.debug(f"Удален файл: {item}")
                else:
                    shutil.rmtree(item)
                    logger.debug(f"Удалена директория: {item}")
                items_cleared += 1
            except FileNotFoundError:
                logger.debug(f"Элемент уже удален: {item}")
            except PermissionError as err:
                logger.error(f"Нет прав для удаления {item}: {err}")
            except (OSError, shutil.Error) as err:
                logger.error(f"Ошибка файловой системы для {item}: {err}")

        logger.info(f"Очищено элементов: {items_cleared}")

    def _download_browser(self) -> Optional[Path]:
        """
        Downloads the Chrome browser package for the current operating system.

        Returns:
            Optional[Path]: The path to the downloaded ZIP file if successful,
            otherwise None.

        Logs:
            Logs the start and completion of the download process, including the
            target URL and path. Logs errors if the download fails.
        """
        url = ApiConfig.BASE_URL + "api/download/"
        if self._system_name.lower() == "windows":
            url += "chrome-win64.zip"
        elif self._system_name.lower() == "linux":
            url += "chrome-linux64.zip"
        elif self._system_name.lower() == "darwin":
            url += "chrome-mac-x64.zip"

        zip_path = self.temp_dir / "chrome.zip"

        logger.info(f"Начинаем загрузку браузера: {url}")
        logger.debug(f"Целевой путь загрузки: {zip_path}")

        try:
            response = requests.get(url, timeout=ApiConfig.REQUEST_TIMEOUT, stream=True)
            response.raise_for_status()

            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info("Браузер успешно загружен")
            return zip_path

        except requests.exceptions.RequestException as err:
            logger.error(f"Ошибка загрузки браузера: {err}")
            return None

    def is_browser_installed(self) -> bool:
        """
        Checks if the browser and its driver are installed and have executable permissions.

        Returns:
            bool: True if both the browser and driver exist and are executable, False otherwise.

        Logs:
            Logs the existence and executable status of the browser and driver.
        """
        driver_exists = self.driver_executable_file.exists()
        browser_exists = self.browser_executable_file.exists()

        driver_executable = os.access(self.driver_executable_file, os.X_OK)
        browser_executable = os.access(self.browser_executable_file, os.X_OK)

        logger.debug(
            f"Проверка установки браузера - "
            f"Драйвер: {'да' if driver_exists else 'нет'} "
            f"({'исполняемый' if driver_executable else 'нет прав'}), "
            f"Браузер: {'да' if browser_exists else 'нет'} "
            f"({'исполняемый' if browser_executable else 'нет прав'})"
        )

        return all([driver_exists, browser_exists])

    def install_browser(self, reinstall: bool = False) -> bool:
        """
        Installs the Chrome browser, optionally reinstalling if specified.

        Args:
            reinstall (bool): If True, forces reinstallation even if the browser
            is already installed.

        Returns:
            bool: True if the installation is successful, False otherwise.

        Logs:
            Logs the start and completion of the installation process, including
            directory creation, clearing of previous installations, downloading,
            extraction, and setting executable permissions. Logs errors if any
            step fails, including download errors, file system errors, and
            permission issues.
        """
        logger.info(f"Начало установки браузера (переустановка={'да' if reinstall else 'нет'})")

        if not reinstall and self.is_browser_installed():
            logger.info("Браузер уже установлен и имеет нужные права, пропускаем установку")
            return True

        # Создаем директории при необходимости
        logger.debug(f"Создание директорий: {self.temp_dir}, {self.browser_dir}")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.browser_dir.mkdir(parents=True, exist_ok=True)

        # Очищаем существующую установку
        logger.info("Очистка предыдущей установки браузера")
        self._clear_browser_directory()

        # Загружаем браузер
        logger.info("Загрузка пакета браузера")
        zip_path = self._download_browser()
        if not zip_path:
            logger.error("Ошибка загрузки браузера, установка прервана")
            return False

        # Распаковываем и очищаем
        logger.info(f"Распаковка пакета браузера из {zip_path} в {self.browser_dir}")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                logger.debug(f"ZIP-архив содержит {len(file_list)} файлов")
                zip_ref.extractall(self.browser_dir)
                logger.debug("Распаковка завершена успешно")

            logger.debug(f"Удаление временного файла: {zip_path}")
            zip_path.unlink(missing_ok=True)

            # Устанавливаем права на исполнение
            logger.info("Установка прав на исполнение для браузера и драйвера")
            if not all([
                self._set_executable_permissions(self.browser_executable_file),
                self._set_executable_permissions(self.driver_executable_file)
            ]):
                logger.error("Не удалось установить права на исполнение")

            # Специальная обработка для macOS
            if self._system_name.lower() == "darwin":
                self._handle_macos_permissions()

            # Проверяем итоговую установку
            if not self.is_browser_installed():
                logger.error("Установка завершена, но браузер или драйвер недоступны")
                return False

            logger.info("Установка браузера успешно завершена")
            return True

        except zipfile.BadZipFile as e:
            logger.error(f"Загруженный файл не является корректным ZIP-архивом: {e}")
            zip_path.unlink(missing_ok=True)
            return False

        except OSError as e:
            logger.error(f"Ошибка файловой системы при распаковке: {e}")
            zip_path.unlink(missing_ok=True)
            return False
