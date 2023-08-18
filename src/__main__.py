import configparser
import os
from pathlib import Path

from archiver import Archiver
from common import is_url
from logger import logger


def main():
    path_dir_root = Path(__file__).parent.parent

    # Load configuration file
    config = configparser.ConfigParser()
    config.read(path_dir_root / "config.ini")

    archiver = Archiver(
        path_dir_archives=os.path.join(
            path_dir_root, config["path"]["path_dir_archives"]
        ),
        path_template=os.path.join(
            path_dir_root,
            config["path"]["path_template"],
        ),
    )

    for username in iter_users(
        path_file_list_users=os.path.join(
            path_dir_root, config["parameters"]["path_file_list_users"]
        )
    ):
        logger.info(f'Archiving user "{username}"')
        archiver.archive_user(username=username)
        break

    archiver.host_local()


def iter_users(path_file_list_users: str) -> str:
    """Iterate through a file containing one username per line.
    Each line can be a valid skyblog URL or a valid skyblog-username.
    """
    with open(path_file_list_users) as fp:
        for username in fp:
            username = username.strip()
            if is_url(username):
                username = username.split("://")[1].split(".")[0]
            yield username


if __name__ == "__main__":
    main()
