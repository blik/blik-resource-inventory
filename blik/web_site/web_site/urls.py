from django.conf.urls import patterns, include, url
from django.conf import settings
from views import SetViews
import os

view = SetViews()

urlpatterns = patterns('',
    (r'^$',view.resource),
    (r'^specification_res/$', view.create),
    (r'^search_spec_res/$', view.search),
    (r'^modal_spec_res/$', view.modal),
    #(r'^edit_spec_res/$', view.edit),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root' : settings.MEDIA_ROOT }),
)