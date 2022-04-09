import requests
from praw.models import Submission
import PySimpleGUI as sg
from PIL import Image, ImageDraw, ImageFont
import io


def get_reddit_preview(submission: Submission):
    if hasattr(submission, "preview"):
        if "images" in submission.preview:
            return download_image_from_url(
                submission.preview["images"][0]["source"]["url"]
            )
    elif hasattr(submission, "media") and submission.media is not None:
        if "oembed" in submission.media:
            return download_image_from_url(submission.media["oembed"]["thumbnail_url"])
    elif submission.selftext:
        return submission.selftext
    elif hasattr(submission, "url") and submission.url:
        return submission.url
    else:
        print(vars(submission))
        return None


def update_preview(submission: Submission, preview_image: sg.Image):
    preview = get_reddit_preview(submission)
    if isinstance(preview, str):
        img = Image.new("RGB", (500, 500), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 16)
        d.text((10, 10), preview, font=font, fill=(0, 0, 0))
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        preview_image.update(source=bio.getvalue())
    elif isinstance(preview, Image.Image):
        preview.thumbnail((500, 500))
        bio = io.BytesIO()
        preview.save(bio, format="PNG")
        preview_image.update(source=bio.getvalue())


def download_image_from_url(url: str) -> Image:
    r = requests.get(url, stream=True)
    if r.ok:
        return Image.open(io.BytesIO(r.content))
    else:
        return None
