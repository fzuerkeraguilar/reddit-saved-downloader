import io
import re
import threading
import time

from bdfr.downloader import RedditDownloader
from bdfr.configuration import Configuration
import logging.handlers


logging.basicConfig()
logger = logging.getLogger()


class BDRFConnector(object):
    def __init__(self):
        self.config = Configuration()
        self.config.authenticate = True
        self.config.file_scheme = "{POSTID}"
        self.config.folder_scheme = "."
        self.config.user = ["me"]
        self.config.saved = True
        self.logger = logging.getLogger("bdfr.oauth2")
        self.log_stream = io.StringIO()
        ch = logging.StreamHandler(self.log_stream)
        self.logger.addHandler(ch)
        self.thread = threading.Thread(target=self.init_downloader)
        self.thread.start()
        time.sleep(1)
        r = re.compile(
            "https:\/\/www\.reddit\.com\/api\/v1\/authorize\?client_id=.*&duration=permanent&redirect_uri=.*&response_type=code&scope=.*&state=.*"
        )
        self.auth_url = re.findall(r, self.log_stream.getvalue())[0]

    def init_downloader(self):
        self.downloader = RedditDownloader(self.config)

    def get_saved_posts(self):
        self.thread.join()
        return self.downloader.reddit_lists

    def download_post(self, submission):
        self.thread.join()
        self.downloader._download_submission(submission)
