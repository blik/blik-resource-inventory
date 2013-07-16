from django.conf.urls import patterns, include, url
from django.conf import settings
from views import SetViews
import os

view = SetViews()

urlpatterns = patterns('',
    (r'^$',view.resource),
    (r'^specification_res/$', view.get_spec),
    (r'^specification_conn/$', view.get_spec),
    (r'^specification_coll/$', view.get_spec),
    (r'^spec_search_res/$', view.search_del),
    (r'^spec_search_conn/$', view.search_del),
    (r'^spec_search_coll/$', view.search_del),

#    (r'^modal_spec_res/$', view.modal),
    (r'^get_connection_type/$', view.get_connection_by_type),  ###
    (r'^get_resource_params/$', view.get_resource_params),  ###
    (r'^get_connection_params/$', view.get_connection_params),  ###
    (r'^get_collection_params/$', view.get_collection_params),  ###
    (r'^get_specification_params/$', view.get_specification_params),  ###


    (r'^tree_menu/$', view.get_param_spec),
    (r'^save_spec/$', view.save_spec),
    (r'^save_element/$', view.save_element),

    (r'^resource/$', view.resource),
    (r'^resource_search/$', view.res_search_del),

    (r'collection/$', view.collection),
    (r'collection_search/$', view.coll_search_del),

    (r'connection_search/$', view.conn_search_del),
    (r'connection/$', view.connection),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root' : settings.MEDIA_ROOT }),
)