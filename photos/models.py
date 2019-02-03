import os
import json
from django.db import models
from django.conf import settings
from os.path import basename, dirname
from django.core.files.storage import get_storage_class
from django.utils.dateparse import parse_datetime, parse_date

from .storage import S3Storage
from .helpers import listdir, listfiles, load_json

storage = S3Storage()


class Album:
    def __init__(self, name, path):
        """Creates an Album object with the provided properties"""
        self.name = name
        self.path = path

    def created(self):
        try:
            self.manifest
        except:
            self.load_manifest()
        return parse_datetime(self.manifest['created'])

    def dropboxcreds(self):
        try:
            self.manifest
        except:
            self.load_manifest()
        return {
            'access_id': self.manifest['dropboxAccessId'],
            'access_token': self.manifest['dropboxAccessToken'],
        }

    def collections(self):
        items = storage.listdir(self.path)
        colls = []
        for item in items[0]:
            name = item.split('/')[1]
            colls.append(Collection(
                album=self.path,
                name=name,
                path=item,
            ))
        return colls

    def load_manifest(self):
        manifest = storage.open(self.path + 'album.json')
        with open(manifest.name, 'r') as f:
            self.manifest = json.load(f)
        os.remove(manifest.name)
        return self.manifest

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.path

    @classmethod
    def all(cls):
        """Returns all albums"""
        items = storage.listdir('/')
        albums = []
        for item in items[0]:
            albums.append(cls(
                name=item[:-1],
                path=item,
            ))
        return albums

    @classmethod
    def get(cls, name):
        """Returns an instance of album for a given album name"""
        if not storage.exists('%s/album.json' % name):
            return None

        return cls(name=name, path=name + '/')


class Collection:
    def __init__(self, album, name, path):
        self.album = album
        self.name = name
        self.path = path
        self.month = parse_date(name + '-01')

    def photos(self):
        files = storage.listfiles(self.path + 'photos/')
        photos = []
        for file in files:
            photos.append(Photo(
                album=self.album,
                collection=self.name,
                name=basename(file['name']),
                size=file['size'],
                path=file['name'],
            ))
        return photos

    def load_manifest(self):
        manifest = storage.open(self.path + 'manifest.json')
        with open(manifest.name, 'r') as f:
            self.manifest = json.load(f)
        os.remove(manifest.name)
        return self.manifest

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.path

    @classmethod
    def get(cls, album, name):
        key = '%s/%s/manifest.json' % (album, name)
        if not storage.exists(key):
            return None

        return cls(
            album=album,
            name=name,
            path='%s/%s/' % (album, name)
        )


class Photo:
    def __init__(self, album, collection, name, size, path):
        self.album = album
        self.collection = collection
        self.name = name
        self.size = size
        self.path = path

    def thumbnail(self):
        thumb = '%s/%s/thumbs/%s' % (self.album, self.collection, self.name)
        return storage.url(thumb)

    def url(self):
        return storage.url(self.path)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s - %s bytes' % (self.path, self.size)
