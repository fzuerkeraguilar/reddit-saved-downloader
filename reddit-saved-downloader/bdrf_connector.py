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
    def __init__(self, download_config_path: str = None):
        self.downloader = None
        self.oauth2_url = None

        self.config = Configuration()
        self.config.authenticate = True
        self.config.file_scheme = "{POSTID}"
        self.config.folder_scheme = "."
        self.config.user = ["me"]
        self.config.saved = True

        bdfr_logger = logging.getLogger("bdfr.oauth2")
        log_stream = io.StringIO()
        ch = logging.StreamHandler(log_stream)
        bdfr_logger.addHandler(ch)
        self.thread = threading.Thread(target=self.init_downloader)
        self.thread.start()

        time.sleep(1)

        r = re.compile(
            r"https://www\.reddit\.com/api/v1/authorize\?client_id=.*&duration=permanent&redirect_uri"
            r"=.*&response_type=code&scope=.*&state=.* "
        )
        matches = re.findall(r, log_stream.getvalue())
        if matches:
            self.oauth2_url = matches[0]
        self.thread.join()
        self.saved_posts = [
            e for e in self.downloader.reddit_lists[0] if isinstance(e, Submission)
        ]

        if download_config_path:
            with open(download_config_path, "r") as f:
                self.download_config = json.load(f)

    def init_downloader(self):
        self.downloader = RedditDownloader(self.config)

    def download_post(self, submission: Submission, user_input: str):
        self.downloader.reddit_lists[0] = [submission]
        if user_input not in self.download_config:
            if os.path.isdir(user_input):
                self.downloader.download_directory = user_input
            else:
                raise Exception("Invalid input")
        else:
            self.downloader.download_directory = self.download_config[user_input]
        print(self.downloader.download_directory)
        self.downloader.download()
