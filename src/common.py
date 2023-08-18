import datetime
import os
import requests


def parse_path(path: str) -> str:
    """Parse a given path with an optional date reformat and an automatic conversion to absolute path."""
    if "{date}" in path:
        path = path.format(date=datetime.datetime.now().date().__str__())
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    return path


def is_url(string: str) -> bool:
    return string.startswith("https://") or string.startswith("http://")


def save_picture(path_dir_output: str, url: str, filename: str = None):
    if filename is None:
        filename = url.split("/")[-1]
    path_file_output = os.path.join(path_dir_output, filename)

    response = requests.get(url)
    if response.status_code == 200:
        with open(path_file_output, "wb") as file:
            file.write(response.content)
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
