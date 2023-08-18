import functools
import os.path
import shutil
from http.server import HTTPServer, SimpleHTTPRequestHandler

import requests

from logger import logger
from core.skyblog_reader import SkyblogReader
from core.skyblog_writer import SkyblogWriter


class Archiver(object):
    """Archivers class
    This class will be used to archive a skyblog and make the link between the user input and the scrapper
    """

    def __init__(self, path_dir_archives: str, path_template: str):
        self.path_dir_archives = path_dir_archives
        self.path_template = path_template
        self.posts = []
        self._max_page_nb = 1
        self._html_first_page = None
        self._username = None
        self._color_bloc_title = None

        # Init paths
        os.makedirs(self.path_dir_archives, exist_ok=True)

    def archive_user(self, username: str):
        path_dir_archive_user = os.path.join(self.path_dir_archives, username)

        if not self.check_user_exists(username):
            logger.warning(f"User does not exists {username}")
            return

        reader = SkyblogReader(
            username=username,
        )
        reader.get()

        writer = SkyblogWriter(
            username=username,
            path_dir_archive_user=path_dir_archive_user,
            path_template=self.path_template,
            articles=reader.articles,
            title=reader.title,
            description=reader.description,
            max_page_number=reader.max_page_number,
            url_profile_picture=reader.url_profile_picture,
            url_background=reader.url_background,
            color_background=reader.color_background,
            color_theme=reader.color_theme,
            color_block_title=reader.color_block_title,
            color_text_title=reader.color_text_title,
            color_articles_background=reader.color_articles_background,
        )
        writer.archive()

    def host_local(self):
        """Host the archive on a local server"""

        handler = functools.partial(
            SimpleHTTPRequestHandler, directory=self.path_dir_archives
        )
        with HTTPServer(("localhost", 8000), handler) as httpd:
            logger.info(
                f"Serving archives at http://{httpd.server_address[0]}:{httpd.server_port}"
            )
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass

    @staticmethod
    def check_user_exists(username: str) -> bool:
        return requests.get(f"https://{username}.skyrock.com").status_code == 200
