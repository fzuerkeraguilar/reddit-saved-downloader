import io
import re
import threading
import time
from praw.models import Submission
from bdfr.downloader import RedditDownloader
from bdfr.configuration import Configuration
import logging.handlers


logging.basicConfig()
logger = logging.getLogger()


class BDRFConnector(object):
    def __init__(self):
        self.downloader = None
        self.oauth2_url = None
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
            r"https://www\.reddit\.com/api/v1/authorize\?client_id=.*&duration=permanent&redirect_uri"
            r"=.*&response_type=code&scope=.*&state=.* "
        )
        matches = re.findall(r, self.log_stream.getvalue())
        if matches:
            self.oauth2_url = matches[0]

    def init_downloader(self):
        self.downloader = RedditDownloader(self.config)

    def get_saved_posts(self):
        self.thread.join()
        return [e for e in self.downloader.reddit_lists[0] if isinstance(e, Submission)]

    def download_post(self, submission: Submission):
        self.thread.join()
        self.downloader._download_submission(submission)
