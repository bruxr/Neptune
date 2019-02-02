from django.http import Http404
from django.shortcuts import render
from django.http import HttpResponse
from .models import Album, Collection
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


@method_decorator(login_required, name='dispatch')
class AlbumsView(TemplateView):
    template_name = 'albums.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['albums'] = Album.get_all()
        return data


@method_decorator(login_required, name='dispatch')
class CollectionsView(TemplateView):
    template_name = 'collections.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        album = Album.get(self.kwargs['album'])
        if album is None:
            raise Http404('Album does not exist')

        data['album'] = album
        data['collections'] = album.get_collections()
        return data


class PhotosView(TemplateView):
    template_name = 'photos.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        coll = Collection.get(self.kwargs['album'], self.kwargs['month'])
        if coll is None:
            raise Http404('Collection does not exist')

        album = Album.get(self.kwargs['album'])

        data['album'] = album
        data['collection'] = coll
        data['photos'] = coll.get_photos()
        return data
