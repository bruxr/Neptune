import json
from django.core.files.storage import default_storage


def listdir(path):
    """
    Returns all subdirectories under the provided path.

    path is a path to the directory to be read/listed,
    relative to the project's root.
    """
    dirs = []
    items = default_storage.listdir(path)
    for folder in items[0]:
        fpath = '%s/%s' % (path, folder)
        dirs.append(fpath)
    return dirs


def listfiles(path):
    """
    Returns all files under the provided path.

    path is a path to the directory to be listed,
    relative to the projects root.
    """
    files = []
    items = default_storage.listdir(path)
    for file in items[1]:
        fpath = '%s/%s' % (path, file)
        files.append(fpath)
    return files


def load_json(file):
    """
    Reads a JSON file and returns a its contents as a dict.

    file is the path to the JSON file.
    """
    manifest = open(file)
    data = json.load(manifest)
    manifest.close()
    return data
