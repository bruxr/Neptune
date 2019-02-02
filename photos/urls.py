from django.urls import path

from . import views

urlpatterns = [
    path('', views.AlbumsView.as_view(), name='albums'),
    path('<slug:album>', views.CollectionsView.as_view(), name='collection'),
    path(
        '<slug:album>/<slug:month>',
        views.PhotosView.as_view(),
        name='photos',
    ),
]
