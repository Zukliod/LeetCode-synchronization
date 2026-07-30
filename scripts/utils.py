import requests
import time


def log(message):
    print(f"[INFO] {message}")


def success(message):
    print(f"[SUCCESS] {message}")


def warning(message):
    print(f"[WARNING] {message}")


def error(message):
    print(f"[ERROR] {message}")


def get_json(url, timeout=10, retries=3):

    for attempt in range(retries):

        try:

            response = requests.get(url, timeout=timeout)

            response.raise_for_status()

            return response.json()

        except Exception as e:

            if attempt == retries - 1:
                raise e

            time.sleep(2)
