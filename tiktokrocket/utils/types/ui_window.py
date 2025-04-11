"""
File: ui_window.py
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
import tkinter as tk


class UiWindow:
    """
    A class that represents a UI window using Tkinter, providing methods to
    initialize, center, and close the window.

    Attributes:
        root (tk.Tk): The root Tkinter window instance.

    Methods:
        __init__(title, geometry, resizable): Initializes the window with a title,
            geometry, and resizable option.
        center_window(): Centers the window on the screen.
        close(): Closes the window.
    """

    def __init__(self, title: str, geometry: str, resizable: bool = False) -> None:
        """
        Initializes a new UI window with the specified title, geometry, and
        resizable option. Sets up the Tkinter root window and centers it on
        the screen.

        Args:
            title (str): The title of the window.
            geometry (str): The size and position of the window in the format 'widthxheight'.
            resizable (bool, optional): Determines if the window can be resized. Defaults to False.
        """
        self.root = tk.Tk()
        self.root.title(string=title)
        self.root.geometry(newGeometry=geometry)
        self.root.resizable(width=resizable, height=resizable)
        self.center_window()

    def center_window(self) -> None:
        """
        Centers the UI window on the screen by calculating and setting
        its position based on the screen and window dimensions.
        """
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def close(self) -> None:
        """
        Closes the UI window by destroying the root Tkinter instance.
        """
        self.root.update()
        self.root.destroy()
