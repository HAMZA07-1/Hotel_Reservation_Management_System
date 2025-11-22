"""
Module: config.py
Date: [insert date]
Programmer(s): Hamza

Brief Description:
This module serves as a centralized configuration file for the application. It defines global constants
and paths that are used across different modules, making it easy to manage and change important settings
like the database file location from a single place.

Important Functions:
- N/A. This module does not contain functions; it only defines variables.

Important Data Structures:
- DB_PATH (str): A string variable that holds the absolute path to the SQLite database file (`hotel.db`).

Algorithms:
- Path Construction: The script uses the `os` module to construct a robust, absolute path to the database
  file. It gets the directory of the `config.py` file itself (`__file__`) and joins it with the database
  filename. This approach ensures that the application can correctly locate the database regardless of the
  current working directory from which the application is launched, which is more reliable than using a
  relative path.
"""
# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hotel.db")
