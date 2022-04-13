import io
import os
import re
import threading
import time
import json
from praw.models import Submission
from bdfr.downloader import RedditDownloader
from bdfr.configuration import Configuration
import logging.handlers

logging.basicConfig()
logger = logging.getLogger()


class BDRFConnector(object):
    def __init__(self):
        self.__saved_posts: list[Submission] = []
        self.downloader: RedditDownloader = None
        self.download_config: dict[str, str] = {}
        self.oauth2_url: str = ""

        self.config: Configuration = Configuration()
        self.config.authenticate = True
        self.config.file_scheme = "{POSTID}"
        self.config.folder_scheme = "."
        self.config.user = ["me"]
        self.config.saved = True

        bdfr_logger = logging.getLogger("bdfr.oauth2")
        log_stream = io.StringIO()
        ch = logging.StreamHandler(log_stream)
        bdfr_logger.addHandler(ch)
        self.init_downloader_thread = threading.Thread(target=self.init_downloader)
        self.init_downloader_thread.start()

        time.sleep(0.5)

        r = re.compile(
            r"https://www\.reddit\.com/api/v1/authorize\?client_id=.*&duration=permanent&redirect_uri"
            r"=.*&response_type=code&scope=.*&state=.*"
        )
        matches = re.findall(r, log_stream.getvalue())
        if matches:
            self.oauth2_url = matches[0]

    def init_downloader(self):
        self.downloader = RedditDownloader(self.config)

    def set_download_config(self, download_config_path: str):
        with open(download_config_path, "r") as f:
            self.download_config = json.load(f)

    def get_saved_posts(self):
        self.init_downloader_thread.join()
        if not self.__saved_posts:
            self.__saved_posts = [
                e for e in self.downloader.reddit_lists[0] if isinstance(e, Submission)
            ]
        return self.__saved_posts

    def download_post(self, submission: Submission, user_input: str):
        self.init_downloader_thread.join()
        self.downloader.reddit_lists[0] = [submission]
        if user_input not in self.download_config:
            if os.path.isdir(user_input):
                self.downloader.download_directory = user_input
            else:
                raise Exception("Invalid input")
        else:
            self.downloader.download_directory = self.download_config[user_input]
        self.downloader.download()
