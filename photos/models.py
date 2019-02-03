import json
from os.path import basename
from django.db import models
from django.conf import settings
from .helpers import listdir, listfiles, load_json
from django.core.files.storage import default_storage
from django.utils.dateparse import parse_datetime, parse_date


class Album:
    def __init__(self, name, base_path, created_at):
        """Creates an Album object with the provided properties"""
        self.name = name
        self.base_path = base_path
        self.created_at = created_at

    def get_collections(self):
        """Returns all photo collections under this album."""
        objects = []
        dirs = listdir(self.base_path)
        for coll in dirs:
            manifest = load_json('media/%s/manifest.json' % coll)
            objects.append(Collection(
                album=self.base_path,
                month=parse_date(manifest['month']),
                created_at=parse_datetime(manifest['created_at']),
                base_path=coll,
            ))
        return objects

    @classmethod
    def get_all(cls):
        """Returns all albums stored under the media/photos/ folder"""
        objects = []
        base_path = 'photos'
        dirs = listdir(base_path)
        for album in dirs:
            data = load_json('media/%s/album.json' % album)
            objects.append(cls(
                name=data['name'],
                base_path=album,
                created_at=parse_datetime(data['created_at']),
            ))
        return objects

    @classmethod
    def get(cls, name):
        """Returns an instance of album for a given album name"""
        album_path = 'photos/%s' % name
        manifest = '%s/album.json' % album_path
        if not default_storage.exists(manifest):
            return None

        data = load_json('media/%s' % manifest)
        return cls(
            name=data['name'],
            base_path=album_path,
            created_at=parse_datetime(data['created_at']),
        )


class Collection:
    def __init__(self, album, month, created_at, base_path):
        self.album = album
        self.month = month
        self.name = month.strftime('%Y-%m')
        self.created_at = created_at
        self.base_path = base_path

    def get_photos(self):
        photos = []
        files = listfiles('%s/photos' % self.base_path)
        for file in files:
            photos.append(Photo(
                album=self.album,
                collection=self.base_path,
                name=basename(file),
                size=default_storage.size(file),
                created_at=default_storage.get_created_time(file),
            ))
        return photos

    @classmethod
    def get(cls, album, month):
        """
        Returns a Collection object for a given album and month.

        album is a string name of the album the collection is under.

        month is a string collection month in YYYY-MM format.
        """
        coll_path = 'photos/%s/%s' % (album, month)
        manifest_path = '%s/manifest.json' % coll_path
        if not default_storage.exists(manifest_path):
            return None

        data = load_json('media/%s' % manifest_path)
        return cls(
            album='photos/%s' % album,
            month=parse_date('%s-01' % month),
            created_at=data['created_at'],
            base_path=coll_path,
        )


class Photo:
    def __init__(self, album, collection, name, size, created_at):
        self.album = album
        self.collection = collection
        self.name = name
        self.size = size
        self.created_at = created_at

    def thumbnail_url(self):
        return '%s%s/thumbnails/%s' % (
            settings.MEDIA_URL,
            self.collection,
            self.name,
        )

    def fullsize_url(self):
        return '%s%s/photos/%s' % (
            settings.MEDIA_URL,
            self.collection,
            self.name,
        )
