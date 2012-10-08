from django.conf.urls import patterns, include, url
from django.conf import settings
from views import SetViews
import os

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

view = SetViews()

urlpatterns = patterns('',
    (r'^$',view.resource),
    (r'^create_spec_res/$', view.create),
    (r'^search_spec_res/$', view.search),
    (r'^modal_spec_res/$', view.modal),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root' : settings.MEDIA_ROOT }),
)

#if settings.DEBUG:
    # static files (images, css, javascript, etc.)
#    urlpatterns += patterns('',
#        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))
