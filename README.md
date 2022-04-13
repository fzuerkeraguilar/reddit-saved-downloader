# reddit-saved-downloader

---
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

Tool to quickly browse and download saved posts from reddit.

After opening the app for the first time you will be asked to login to reddit through the browser.
The application will list all saved posts and allow you to download them by pressing the enter key.
You can navigate through the saved posts by using the up and down arrow keys.

The download location can be chosen manually or by using shortcuts supplied in a json file.
The json file must be made up of simple key-value pairs. The key is the shortcut and the value is the download location.
Please look at the [example_download_config.json](./reddit-saved-downloader/example_download_config.json) file for an example.
A given input is first checked against the shortcuts and if it matches a shortcut the corresponding download location is used.