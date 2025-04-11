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
import zipfile
import platform
import os
import stat
from pathlib import Path
from typing import Optional

import requests
from loguru import logger

from tiktokrocket.data.config import ApiConfig


class Updater:
    """
    Класс для управления установкой браузера Chrome.
    Обеспечивает проверку существующей установки, очистку директорий,
    загрузку последней версии и установку.
    """

    def __init__(
            self,
            data_dir: Path,
            browser_dir: Path,
            driver_executable_file: Path,
            browser_executable_file: Path,
    ):
        self.data_dir = data_dir
        self.browser_dir = browser_dir
        self.driver_executable_file = driver_executable_file
        self.browser_executable_file = browser_executable_file
        self._system_name = platform.system()

    def _set_executable_permissions(self, file_path: Path) -> bool:
        """
        Устанавливает права на исполнение для файла (chmod +x)

        Args:
            file_path: Путь к файлу

        Returns:
            bool: True если права установлены успешно, False в случае ошибки
        """
        try:
            if not file_path.exists():
                logger.error(f"Файл не существует: {file_path}")
                return False

            current_mode = os.stat(file_path).st_mode
            os.chmod(file_path, current_mode | stat.S_IEXEC)
            logger.debug(f"Установлены права на исполнение для: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка установки прав для {file_path}: {e}")
            return False

    def is_browser_installed(self) -> bool:
        """
        Проверяет установлен ли браузер и драйвер.

        Returns:
            bool: True если оба файла существуют и исполняемы, иначе False
        """
        driver_exists = self.driver_executable_file.exists()
        browser_exists = self.browser_executable_file.exists()

        # Проверяем права на исполнение
        driver_executable = os.access(self.driver_executable_file, os.X_OK)
        browser_executable = os.access(self.browser_executable_file, os.X_OK)

        logger.debug(
            f"Проверка установки браузера - "
            f"Драйвер: {'да' if driver_exists else 'нет'} ({'исполняемый' if driver_executable else 'нет прав'}), "
            f"Браузер: {'да' if browser_exists else 'нет'} ({'исполняемый' if browser_executable else 'нет прав'})"
        )

        return all([driver_exists, browser_exists, driver_executable, browser_executable])

    def _clear_browser_directory(self) -> None:
        """
        Очищает директорию браузера.
        Если директория не существует, ничего не делает.
        """
        if not self.browser_dir.exists():
            logger.debug(f"Директория браузера {self.browser_dir} не существует, очистка не требуется")
            return

        logger.info(f"Очистка директории браузера: {self.browser_dir}")
        items_cleared = 0

        for item in self.browser_dir.iterdir():
            try:
                if item.is_file():
                    item.unlink(missing_ok=True)
                    logger.debug(f"Удален файл: {item}")
                else:
                    import shutil
                    shutil.rmtree(item)
                    logger.debug(f"Удалена директория: {item}")
                items_cleared += 1
            except Exception as e:
                logger.error(f"Ошибка при удалении {item}: {e}")

        logger.info(f"Очищено элементов: {items_cleared}")

    def _download_browser(self, storage_dir: Path) -> Optional[Path]:
        """
        Загружает пакет браузера с сервера.

        Args:
            storage_dir: Директория для сохранения файла

        Returns:
            Путь к загруженному файлу или None при ошибке
        """
        url = ApiConfig.BASE_URL + "api/download/"
        if self._system_name.lower() == "windows":
            url += "chrome-win64.zip"
        elif self._system_name.lower() == "linux":
            url += "chrome-linux64.zip"
        elif self._system_name.lower() == "darwin":
            url += "chrome-mac-x64.zip"

        zip_path = storage_dir / "chrome.zip"

        logger.info(f"Начало загрузки браузера из {url}")
        logger.debug(f"Целевой путь загрузки: {zip_path}")

        try:
            logger.debug(f"Запрос с таймаутом: {ApiConfig.REQUEST_TIMEOUT}")
            response = requests.get(
                url,
                timeout=ApiConfig.REQUEST_TIMEOUT,
                stream=True
            )
            response.raise_for_status()

            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Браузер успешно загружен в {zip_path}")
            return zip_path

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка загрузки браузера: {e}")
            return None

    def _handle_macOS_permissions(self) -> bool:
        """
        Специальная обработка прав для macOS (включая Gatekeeper)

        Returns:
            bool: True если обработка прошла успешно
        """
        if self._system_name.lower() != "darwin":
            return True

        try:
            # Удаляем атрибут карантина (Gatekeeper)
            os.system(f'xattr -d com.apple.quarantine "{self.browser_executable_file}"')
            os.system(f'xattr -d com.apple.quarantine "{self.driver_executable_file}"')
            logger.debug("Атрибуты карантина macOS успешно удалены")
            return True
        except Exception as e:
            logger.warning(f"Не удалось обработать атрибуты macOS: {e}")
            return False

    def install_browser(self, reinstall: bool = False) -> bool:
        """
        Устанавливает браузер Chrome.

        Args:
            reinstall: Принудительная переустановка, даже если браузер установлен

        Returns:
            bool: True если установка успешна, иначе False
        """
        logger.info(f"Начало установки браузера (переустановка={'да' if reinstall else 'нет'})")

        if not reinstall and self.is_browser_installed():
            logger.info("Браузер уже установлен и имеет нужные права, пропускаем установку")
            return True

        # Создаем директории при необходимости
        temp_dir = self.data_dir / "temp"
        logger.debug(f"Создание директорий: {temp_dir}, {self.browser_dir}")

        temp_dir.mkdir(parents=True, exist_ok=True)
        self.browser_dir.mkdir(parents=True, exist_ok=True)

        # Очищаем существующую установку
        logger.info("Очистка предыдущей установки браузера")
        self._clear_browser_directory()

        # Загружаем браузер
        logger.info("Загрузка пакета браузера")
        zip_path = self._download_browser(temp_dir)
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
                return False

            # Специальная обработка для macOS
            if self._system_name.lower() == "darwin":
                self._handle_macOS_permissions()

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
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при установке: {e}")
            zip_path.unlink(missing_ok=True)
            return False
