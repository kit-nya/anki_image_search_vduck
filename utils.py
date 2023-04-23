import os
from os.path import dirname, abspath, realpath
import importlib
from tempfile import mkstemp
from uuid import uuid4

import requests
from aqt import mw


CURRENT_DIR = dirname(abspath(realpath(__file__)))


def path_to(*args):
    return os.path.join(CURRENT_DIR, *args)


def get_config():
    return mw.addonManager.getConfig(__name__)


def get_note_query(note):
    field_names = mw.col.models.field_names(note.note_type())
    query_field = field_names.index(get_config()["query_field"])
    return note.fields[query_field]


def get_note_image_field_index(note):
    field_names = mw.col.models.field_names(note.note_type())
    return field_names.index(get_config()["image_field"])


def save_file_to_library(editor, image_url):
    # Set a user agent to avoid 403 errors
    try:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0"}
        response = requests.get(image_url, headers=headers, timeout=5)
        if response.status_code != 200:
            report("Couldn't download image from URL '{}' :(".format(image_url))
            return None
        # Get file type from response
    except requests.exceptions.RequestException as e:
        report("Couldn't download image from URL '{}' :(".format(image_url))
        return None
    file_extension = response.headers["Content-Type"].split("/")[-1]
    (i_file, temp_path) = mkstemp(prefix=str(uuid4()), suffix=file_extension)
    os.write(i_file, response.content)
    os.close(i_file)
    result_filename = editor.mw.col.media.add_file(temp_path)
    try:
        os.unlink(temp_path)
    except:
        pass
    return result_filename


def image_tag(image_url):
    attrs = {"src": image_url, "class": "imgsearch"}
    tag_components = ['{}="{}"'.format(key, val) for key, val in attrs.items()]
    return "<img " + " ".join(tag_components) + " />"


def report(text):
    if importlib.util.find_spec("aqt"):
        from aqt.utils import showWarning
        showWarning(text, title="Anki Image Search vDuck")
    else:
        print(text)
