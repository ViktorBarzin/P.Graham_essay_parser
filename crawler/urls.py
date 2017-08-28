from django.conf.urls import include, url
from .views import download_essays_view


urlpatterns = [
    url(r'^$', download_essays_view, name='download_essays'),
]
