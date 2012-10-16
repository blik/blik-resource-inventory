from django.conf.urls import patterns, include, url
from django.conf import settings
from views import SetViews
import os

view = SetViews()

urlpatterns = patterns('',
    (r'^$',view.resource),
    (r'^specification_res/$', view.create_update),
    (r'^specification_conn/$', view.create_update),
    (r'^specification_coll/$', view.create_update),
    (r'^spec_search_res/$', view.search_del),
    (r'^modal_spec_res/$', view.modal),
    (r'^spec_search_conn/$', view.search_del),
    (r'^spec_search_coll/$', view.search_del),
    #(r'^edit_spec_res/$', view.edit),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root' : settings.MEDIA_ROOT }),
)