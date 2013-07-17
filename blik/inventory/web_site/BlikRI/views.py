# -*- coding: utf-8 -*-

import os
import ast
import json

from blik.inventory.api.management_api import ManagementAPI
from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
from blik.inventory.api.collection_oper_api import CollectionOperationalAPI
from blik.inventory.api.connection_oper_api import ConnectionOperationalAPI, CONNECTED, CONNECTING
from resource_api import ResourceAPI
from collection_api import CollectionAPI
from connection_api import ConnectionAPI

from blik.inventory.backend.common import CommonDatabaseAPI

from blik.inventory.core.base_entities import *

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils import simplejson
from django.conf import settings

ELEM_TYPES = {'IS_RES': 'resource',
              'IS_CONN': 'connection',
              'IS_COLL': 'collection'}

SEARCH_PAGE = {'resource': 'spec_search_res',
               'connection': 'spec_search_conn',
               'collection': 'spec_search_coll'}

SPEC_TYPE = {'specification_res': 'resource',
             'specification_conn': 'connection',
             'specification_coll': 'collection'} 


class SetViews():
    def __init__(self):
        self.specification = ManagementAPI()

    def conn_search_del(self, request):
        """ search and delete connections """
        conn = ConnectionAPI()
        conn_list = []
        if request.GET and not request.POST:
            conn_list = conn.search(request.GET)
        elif request.POST:
            conn_list = conn.delete(request.POST.get('del_id', None), request.GET)

        return render_to_response('connection_search.html',{'res_list': conn_list,
                                                            'elem_type': ELEM_TYPES['IS_CONN']})

    def connection(self, request):
        """get connection for create/modify """
        conn_id = request.GET.get('elem_id',)
        if conn_id:
            return render_to_response('connection.html', { 'conn_id': conn_id,})

        # create connection
        conn_spec_list = self._search_spec(ELEM_TYPES['IS_CONN'])
        return  render_to_response('connection_create.html', { 'items_list': conn_spec_list})

    def get_connection_params(self, request):
        """ implement GET method """
        if request.GET.get('spec_id', None):
            connection = ConnectionOperationalAPI()
            conn_info = connection.getConnectionInfo(request.GET['spec_id']).to_dict()
            conn_spec = self._search_spec(ELEM_TYPES['IS_CONN'], conn_info['specification_name'])[0]
        connection = ConnectionOperationalAPI()
        conn_filter = {'specification_name': conn_name}

        conn_list = self._search_elem(conn_filter, connection)
        return render_to_response('connection_search.html', {'res_list': conn_list, 'elem_type': ELEM_TYPES['IS_CONN']},
                                  context_instance=RequestContext(request))

    def connection(self, request):
        """ Get connection for create """
        conn_spec_list = self._search_spec(ELEM_TYPES['IS_CONN'])
        return render_to_response('connection.html', {'items_list': conn_spec_list},
                                  context_instance=RequestContext(request))

    def coll_search_del(self, request):
        """ Search and delete collections """

        connected_type = conn_spec['connected_type']
        connecting_type = conn_spec['connecting_type']
        resource = ResourceOperationalAPI()

        res_filter = {'specification_name': str(connecting_type)}
        raw_connecting_res_list = self._search_elem(res_filter, resource)

        connecting_res_list = []
        if raw_connecting_res_list:
            for res in raw_connecting_res_list:
                connecting_res_dict = dict()
                connecting_res_dict['connecting_res_id'] = res['id']
                connecting_res_dict['res_name'] = res['specification_name']
                connecting_res_list.append(connecting_res_dict)

        res_filter = {'specification_name': str(connected_type)}
        raw_connected_res_list = self._search_elem(res_filter, resource)
        connected_res_list = []
        if raw_connected_res_list:
            for res in raw_connected_res_list:
                connected_res_dict = dict()
                connected_res_dict['connected_res_id'] = res['id']
                connected_res_dict['res_name'] = res['specification_name']
                connected_res_list.append(connected_res_dict)

        # for TreeMenu
        spec_params_json = json.dumps(conn_spec['params_spec'])
        to_text = spec_params_json.replace('param_name','text')
        items = to_text.replace('children_spec','items')

        json_data = {'conn_spec': conn_spec['params_spec'],
                     'conn_info': conn_info,
                     'items': json.loads(items),
                     'connected_type': conn_spec.get('connected_type', None),
                     'connecting_type': conn_spec.get('connecting_type', None),
                     'connected_res_list': connected_res_list,
                     'connecting_res_list': connecting_res_list}
        return HttpResponse(json.dumps(json_data), mimetype="application/json")

    #return HttpResponse()

    def coll_search_del(self, request):
        """search and delete collections"""
        coll = CollectionAPI()
        coll_list = []
        if request.GET and not request.POST:
            coll_list = coll.search(request.GET)
        elif request.POST:
            coll_list = coll.delete(request.POST.get('del_id', None), request.GET)
        return render_to_response('collection_search.html', {'res_list': coll_list,
                                                             'elem_type': ELEM_TYPES['IS_COLL']})
    def collection(self, request):
        """get collection for modify"""
        if request.GET.get('elem_id', None):
=======
                                                             'allowed_types': allowed_types,
                                                             'elem_type': ELEM_TYPES['IS_COLL']},
                                  context_instance=RequestContext(request))

    def collection(self, request):
        """ Get collection for modify """
>>>>>>> 93012f740efc69a9841645c1062564e88025181a

            return render_to_response('collection.html', {'coll_id': request.GET['elem_id']})

        coll_spec_list = self._search_spec(ELEM_TYPES['IS_COLL'])
        return  render_to_response('collection_create.html', { 'items_list': coll_spec_list})

    def get_collection_params(self, request):
        """ implement GET method """
        if request.GET.get('coll_id', None):
            collection = CollectionOperationalAPI()

            coll_info = collection.getCollectionInfo(request.GET['coll_id']).to_dict()
            coll_spec = self._search_spec(ELEM_TYPES['IS_COLL'], coll_info['specification_name'])[0]

            # for TreeMenu
            spec_params_json = json.dumps(coll_spec['params_spec'])
<<<<<<< HEAD
            to_text = spec_params_json.replace('param_name','text')
            items = to_text.replace('children_spec','items')

            json_data = {'coll_spec': coll_spec['params_spec'],
                         'coll_info': coll_info,
                         'allowed_types': coll_spec['allowed_types'],
                         'items': json.loads(items)}
            return HttpResponse(json.dumps(json_data), mimetype="application/json")

        return HttpResponse()

    def resource(self,request):
        """Render resource page for creating and modifying """
        # get resource for modify
        if request.GET.get('elem_id', None):
            # get connections list
            connection = ConnectionAPI()
            conn_list_raw = connection.search()
            conn_list = []
            if conn_list_raw:
                for conn in conn_list_raw:
                    conn_list.append(conn['specification_name'])

            return render_to_response('resource.html', { 'res_id': request.GET['elem_id'],
                                                         'conn_list': list(set(conn_list))})

        # get specs for creating resource
        res_spec_list = self._search_spec(ELEM_TYPES['IS_RES'])
=======

            to_text = spec_params_json.replace('param_name', 'text')
            items = to_text.replace('children_spec', 'items')
            return render_to_response('collection.html', {'coll_id': coll['_id'],
                                                          'coll_desc': coll['description'],
                                                          'coll_name': coll['specification_name'],

                                                          # for init() on base.html
                                                          'spec_param_list': json.dumps(coll_spec),
                                                          'items': items,
                                                          'parent_spec': coll['specification_name'],
                                                          'type': 'element',
                                                          'res_param_dict': coll_params_json,
                                                          'allowed_coll': [],
                                                          'assigned_coll': []},
                                      context_instance=RequestContext(request))

        coll_spec_list = self._search_spec(ELEM_TYPES['IS_COLL'])
        return  render_to_response('collection.html', {'items_list': coll_spec_list},
                                   context_instance=RequestContext(request))

    def resource(self, request):
        """ Render resource page for creating and modifying """
>>>>>>> 93012f740efc69a9841645c1062564e88025181a

        return render_to_response('resource_create.html', { 'items_list': res_spec_list})

    def get_resource_params(self, request):
        """implement GET method for get resource info """
        #res_id = request.GET.get('elem_id', None)
        if request.GET.get('elem_id', None):
            res_id = request.GET['elem_id']
            resource = ResourceOperationalAPI()

            res_info = resource.getResourceInfo(res_id).to_dict()
            res_spec = self._search_spec(ELEM_TYPES['IS_RES'], res_info['specification_name'])[0]

            # find allowed collections for resource
            spec_filter = {'allowed_types': str(res_info['specification_name'])}
            raw_spec_list = self.specification.findSpecification(ELEM_TYPES['IS_COLL'], spec_filter)
            allowed_spec_coll_list = []
            if raw_spec_list:
                for spec in raw_spec_list:
                    s = spec.to_dict()
                    allowed_spec_coll_list.append(s['type_name'])

<<<<<<< HEAD
            # find created collections
            collection  = CollectionOperationalAPI()
=======
            # find collections
            collection = CollectionOperationalAPI()
>>>>>>> 93012f740efc69a9841645c1062564e88025181a
            coll_filter = {'specification_name__in': allowed_spec_coll_list}
            raw_allow_coll_list = collection.findCollections(coll_filter)
            allow_coll_list = []
            for coll in raw_allow_coll_list:
                c = coll.to_dict()
                d = dict()
                d['value'] = c.pop('_id')
                d['content'] = c.pop('specification_name')
                allow_coll_list.append(d)
            # find assigned resource in collections
            coll_filter = {'resources': res_id}
            raw_coll_list = collection.findCollections(coll_filter)
            assigned_coll_list = []
            for coll in raw_coll_list:
                c = coll.to_dict()
                assigned_coll_list.append(c['_id'])

            # treeMenu
            spec_params_json = json.dumps(res_spec['params_spec'])
<<<<<<< HEAD
            to_text = spec_params_json.replace('param_name','text')
            items = to_text.replace('children_spec','items')

            json_data = {'res_spec': res_spec['params_spec'],
                         'res_info': res_info,
                         'items': json.loads(items),
                         'allowed_coll': allow_coll_list,
                         'assigned_coll': assigned_coll_list}

            return HttpResponse(json.dumps(json_data), mimetype="application/json")

        return HttpResponse()
=======

            to_text = spec_params_json.replace('param_name', 'text')
            items = to_text.replace('children_spec', 'items')

            return render_to_response('resource.html', {'res_id': res['_id'],
                                                        'res_status': res['resource_status'],
                                                        'res_desc': res['description'],
                                                        'res_sys': res['external_system'],
                                                        'res_loc': res['location'],
                                                        'res_dep': res['department'],
                                                        'res_own': res['owner'],

                                                        # for init() on base.html
                                                        'spec_param_list': json.dumps(res_spec),
                                                        'items': items,
                                                        'parent_spec': res['specification_name'],
                                                        'type': 'element',
                                                        'res_param_dict': res_params_json,
                                                        'allowed_coll': json.dumps(allow_coll_list),
                                                        'assigned_coll': assigned_coll_list},
                                      context_instance=RequestContext(request))
        # get specs for creating resource
        res_spec_list = self._search_spec(ELEM_TYPES['IS_RES'])

        return render_to_response('resource.html', {'items_list': res_spec_list},
                                  context_instance=RequestContext(request))
>>>>>>> 93012f740efc69a9841645c1062564e88025181a

    def res_search_del(self, request):
        """ Searching and deleting resource """
        res = ResourceAPI()
        if request.GET and not request.POST:

            res_list = res.search_resource(request.GET)
            #json_data = {'res_list': res_list, 'elem_type': ELEM_TYPES['IS_RES']}
            #return HttpResponse(json.dumps(json_data), mimetype="application/json")

            return render_to_response('resource_search.html', {'res_list': res_list,
                                                               'elem_type': ELEM_TYPES['IS_RES']})

        elif request.POST:
            res_list = res.del_resource(request.POST.get('del_id',), request.GET)

            return render_to_response('resource_search.html', {'res_list': res_list,
                                                               'elem_type': ELEM_TYPES['IS_RES']})

<<<<<<< HEAD
        # render empty page
        return render_to_response('resource_search.html', {'res_list': [], 'elem_type': ELEM_TYPES['IS_RES']})
=======
            res_list = self._search_elem(resource_filter, resource)

        return render_to_response('resource_search.html', {'res_list': res_list, 'elem_type': ELEM_TYPES['IS_RES']},
                                  context_instance=RequestContext(request))
>>>>>>> 93012f740efc69a9841645c1062564e88025181a

    def _search_elem(self, resource_filter, element):
        obj_list = []
        if isinstance(element, ResourceOperationalAPI):
            obj_list = element.findResources(resource_filter)
        elif isinstance(element, CollectionOperationalAPI):
            obj_list = element.findCollections(resource_filter)
        elif isinstance(element, ConnectionOperationalAPI):
            obj_list = element.findConnection(resource_filter)

        elems_list = []
        for item in obj_list:
            s = item.to_dict()
            s['id'] = s.pop('_id')
            elems_list.append(s)

        return elems_list

    def save_element(self, request):
        """ Saving and updating elements """
        elem_type = request.POST.get('res_name',)
        elem_desc = request.POST.get('elem_desc',) # must be elem_desc
        elem_id = request.POST.get('elem_id',)

        res_status = request.POST.get('res_status',)
        res_sys = request.POST.get('res_sys',)
        res_loc = request.POST.get('res_loc',)
        res_dep = request.POST.get('res_dep',)
        res_own = request.POST.get('res_own',)
        res_type = request.POST.get('res_type',)

        raw_param_res = request.POST.get('res_param',)

        old_assigned_to_coll = request.POST.get('old_assigned_to_coll',)
        new_assigned_to_coll = request.POST.get('new_assigned_to_coll',)
        if old_assigned_to_coll:
            old_assigned_to_coll = json.loads(old_assigned_to_coll)
        if new_assigned_to_coll:
            new_assigned_to_coll = json.loads(new_assigned_to_coll)

        #print request.POST
        # resource
        if res_type == ELEM_TYPES['IS_RES']:
            resource = ResourceOperationalAPI()

            spec = self._search_spec(ELEM_TYPES['IS_RES'], elem_type)[0]
            Resource.setup_specification([ResourceSpecification(spec)])

            if elem_id:
                self._update_collections(old_assigned_to_coll, new_assigned_to_coll, elem_id)
                resource.updateResource(elem_id, res_status, elem_desc, res_sys, res_loc, res_dep, res_own,
                                        additional_parameters=json.loads(raw_param_res))
            else:
                resource.createResource(elem_type, res_status, elem_desc, res_sys, res_loc, res_dep, res_own,
                                        additional_parameters=json.loads(raw_param_res))
            return HttpResponse()

        # collections
        if res_type == ELEM_TYPES['IS_COLL']:
            collection = CollectionOperationalAPI()
            coll_spec = self._search_spec(ELEM_TYPES['IS_COLL'], elem_type)[0]
            Collection.setup_specification([CollectionSpecification(coll_spec)])

            if elem_id:
                collection.updateCollectionInfo(elem_id, elem_desc, additional_parameters=json.loads(raw_param_res))
            else:
                collection.createCollection(elem_type, elem_desc, additional_parameters=json.loads(raw_param_res))

            return HttpResponse()

        # connections
        if res_type == ELEM_TYPES['IS_CONN']:
            connection = ConnectionOperationalAPI()

            connecting_res_id = request.POST.get('connecting_res_id',)
            connected_res_id = request.POST.get('connected_res_id',)
<<<<<<< HEAD

            conn_spec = self._search_spec(ELEM_TYPES['IS_CONN'], elem_type)[0]
            Connection.setup_specification([ConnectionSpecification(conn_spec)])

            if elem_id:
                connection.updateConnection(elem_id, elem_desc, connecting_res_id, connected_res_id,
                                            additional_parameters=json.loads(raw_param_res))
            else:
                connection.connectResources(elem_type, connecting_res_id, connected_res_id, elem_desc,
=======
            connecting_res = resource.getResourceInfo(connecting_res_id).to_dict()
            res_spec = self._search_spec(ELEM_TYPES['IS_RES'], connecting_res['specification_name'])[0]
            Resource.setup_specification([ResourceSpecification(res_spec)])

            connected_res  = resource.getResourceInfo(connected_res_id).to_dict()
            res_spec = self._search_spec(ELEM_TYPES['IS_RES'], connected_res['specification_name'])[0]
            Resource.setup_specification([ResourceSpecification(res_spec)])

            connection = ConnectionOperationalAPI()
            conn_spec = self._search_spec(ELEM_TYPES['IS_CONN'], elem_type)[0]
            Connection.setup_specification([ConnectionSpecification(conn_spec)])

            connection.connectResources(elem_type, connecting_res_id, connected_res_id, elem_desc,
>>>>>>> 93012f740efc69a9841645c1062564e88025181a
                                        **json.loads(raw_param_res))

            return HttpResponse()

    def _update_collections(self, old_assigned_to_coll, new_assigned_to_coll, res_id):
<<<<<<< HEAD
        """append or remove resource from collections
        """
=======
        """Append or remove resource from collections"""
>>>>>>> 93012f740efc69a9841645c1062564e88025181a
        diff_list = set(old_assigned_to_coll)
        new_list = diff_list.symmetric_difference(new_assigned_to_coll)
        collection = CollectionOperationalAPI()

        for coll_id in new_list:
            if coll_id in new_assigned_to_coll:
                coll = collection.getCollectionInfo(coll_id).to_dict()
                coll_spec = self._search_spec(ELEM_TYPES['IS_COLL'], coll['specification_name'])[0]
                Collection.setup_specification([CollectionSpecification(coll_spec)])

                collection.appendResourceToCollection(coll_id, res_id)
            elif coll_id in old_assigned_to_coll:
                collection.removeResourceFromCollection(coll_id, res_id)

    def save_spec(self, request):
        if request.is_ajax():
            spec_id = request.POST.get('spec_id',)
            spec_name = request.POST.get('spec_name',)
            spec_type = request.POST.get('spec_type',)
            description = request.POST.get('spec_desc',)
            spec_parent = request.POST.get('parent_spec',)
            connion_type = request.POST.get('connion_type',)
            conned_type = request.POST.get('conned_type',)
            allowed_types = request.POST.get('allowed_types',)
            raw_param_spec = request.POST.get('param_spec',)

            params_spec = json.loads(raw_param_spec)

            if spec_type == ELEM_TYPES['IS_RES']:
                if spec_id:
                    self.specification.updateSpecification(spec_id, spec_name, spec_parent, spec_type, description,
                                                           params_spec=params_spec)
                else:
                    self.specification.createSpecification(spec_name, spec_parent, spec_type, description,
                                                           params_spec=params_spec)
            elif spec_type == ELEM_TYPES['IS_CONN']:
                if spec_id:
                    self.specification.updateSpecification(spec_id, spec_name, spec_parent, spec_type, description,
                                                           connecting_type=connion_type, connected_type=conned_type,
                                                           params_spec=params_spec)
                else:
                    self.specification.createSpecification(spec_name, spec_parent, spec_type, description,
                                                           connecting_type=connion_type, connected_type=conned_type,
                                                           params_spec=params_spec)
            elif spec_type == ELEM_TYPES['IS_COLL']:
                all_type = allowed_types.split(',')
                if spec_id:
                    self.specification.updateSpecification(spec_id, spec_name, spec_parent, spec_type, description,
                                                           allowed_types=all_type, params_spec=params_spec)
                else:
                    self.specification.createSpecification(spec_name, spec_parent, spec_type, description,
                                                           allowed_types=all_type, params_spec=params_spec)

            return HttpResponse()

<<<<<<< HEAD
#    def modal(self,request):
#        cookies = request.META.get('HTTP_COOKIE')
#        spec_id = request.COOKIES['spec_id']
#
#        raw_spec = self.specification.getSpecification(spec_id).to_dict()
#        spec_param_json = json.dumps(raw_spec['params_spec'])
#
#        to_text = spec_param_json.replace('param_name','text')
#        items = to_text.replace('children_spec','items')
#
#        return render_to_response('modal_spec_res.html', {'items': items})

    def get_connection_by_type(self, request):
        """ get connection type for resource """
        if request.is_ajax():
            res_id = request.GET.get('elem_id', None)
            conn_type = request.GET.get('conn_id', None)

            connection = ConnectionOperationalAPI()
            resource = ResourceOperationalAPI()
            #print res_id, conn_type
            connected_res = connection.getLinkedResources(res_id, conn_type=conn_type, conn_direction=CONNECTED)
            connecting_res = connection.getLinkedResources(res_id, conn_type=conn_type, conn_direction=CONNECTING)

            connected_list = []
            for tt in connecting_res:
                conn_res_id = tt.to_dict()['connected_resource']
                res_info = resource.getResourceInfo(conn_res_id).to_dict()
               # print 'connected',res_info
                connected_list.append(res_info['specification_name'])

            connecting_list = []
            for tt in connected_res:
                conn_res_id = tt.to_dict()['connecting_resource']
                res_info = resource.getResourceInfo(conn_res_id).to_dict()
                #print 'connecting',res_info
                connecting_list.append(res_info['specification_name'])
            #print 'connected_list',connected_list
            return HttpResponse(json.dumps({'connecting_list': connecting_list,
                                            'connected_list': connected_list}), mimetype="application/json")

    def get_param_spec(self,request):
=======
    def modal(self, request):
        cookies = request.META.get('HTTP_COOKIE')
        spec_id = request.COOKIES['spec_id']

        raw_spec = self.specification.getSpecification(spec_id).to_dict()
        spec_param_json = json.dumps(raw_spec['params_spec'])

        to_text = spec_param_json.replace('param_name', 'text')
        items = to_text.replace('children_spec', 'items')

        return render_to_response('modal_spec_res.html', {'items': items}, context_instance=RequestContext(request))

    def get_param_spec(self, request):
        #spec_id = request.GET.get('spec_id',)
        #print request

        #clear data in file
        #open('./web_site/media/tree_menu.json', 'w').close()
        #open('./web_site/media/spec_param_list.json', 'w').close()
        #print 'ajax'

>>>>>>> 93012f740efc69a9841645c1062564e88025181a
        if request.is_ajax():
            #print request
            spec_id = request.GET.get('spec_id',)

            raw_spec = self.specification.getSpecification(spec_id).to_dict()
            #spec_param_json = json.dumps(raw_spec['params_spec'])

            #print raw_spec
            json_params = {}
            # for connections
            if raw_spec['spec_type'] == ELEM_TYPES['IS_CONN']:
                connected_type = raw_spec['connected_type']
                connecting_type = raw_spec['connecting_type']
                #print raw_spec
                resource = ResourceOperationalAPI()

                res_filter = {'specification_name': str(connecting_type)}
                raw_connecting_res_list = self._search_elem(res_filter, resource)

                if raw_connecting_res_list:
                    connecting_res_list = []
                    for res in raw_connecting_res_list:
                        connecting_res_dict = dict()
                        connecting_res_dict['connecting_res_id'] = res['id']
                        connecting_res_dict['res_name'] = res['specification_name']
                        connecting_res_list.append(connecting_res_dict)
<<<<<<< HEAD
                    json_params['connecting_res_list'] = connecting_res_list
=======
#                    with open('./web_blik/media/connecting_res_list.json', 'w') as f: f.write(json.dumps(connecting_res_list))
                    with open(os.path.join(settings.MEDIA_ROOT, "connecting_res_list.json"), "w") as f:
                        f.write(json.dumps(connecting_res_list))
>>>>>>> 93012f740efc69a9841645c1062564e88025181a

                res_filter = {'specification_name': str(connected_type)}
                raw_connected_res_list = self._search_elem(res_filter, resource)
                if raw_connected_res_list:
                    connected_res_list = []
                    for res in raw_connected_res_list:
                        connected_res_dict = dict()
                        connected_res_dict['connected_res_id'] = res['id']
                        connected_res_dict['res_name'] = res['specification_name']
                        connected_res_list.append(connected_res_dict)
<<<<<<< HEAD
                    json_params['connected_res_list'] = connected_res_list

        # for create specifications
            load_page =  request.META.get('HTTP_REFERER').split('/')
            spec_param_json = json.dumps(raw_spec)
=======
#                    with open('./web_blik/media/connected_res_list.json', 'w') as f: f.write(json.dumps(connected_res_list))
                    with open(os.path.join(settings.MEDIA_ROOT, "connected_res_list.json"), "w") as f:
                        f.write(json.dumps(connected_res_list))

        # for create specifications
            load_page = request.META.get('HTTP_REFERER').split('/')
>>>>>>> 93012f740efc69a9841645c1062564e88025181a
            if load_page[3] in SPEC_TYPE.keys():
                to_text = spec_param_json.replace('param_name','text')
                items = to_text.replace('children_spec','items')

<<<<<<< HEAD
                #with open('./web_site/media/tree_menu.json', 'w') as f: f.write(items)
                #with open('./web_site/media/spec_param_list.json', 'w') as f: f.write(spec_param_json)
                json_params = {'spec_param_list': json.loads(spec_param_json), 'params_list': json.loads(items)}
                return HttpResponse(json.dumps(json_params), mimetype="application/json")
=======
#                with open('./web_blik/media/tree_menu.json', 'w') as f: f.write(items)
                with open(os.path.join(settings.MEDIA_ROOT, "tree_menu.json"), 'w') as f:
                    f.write(items)
#                with open('./web_blik/media/spec_param_list.json', 'w') as f: f.write(spec_param_json)
                with open(os.path.join(settings.MEDIA_ROOT, "spec_param_list.json"), 'w') as f:
                    f.write(spec_param_json)

                return HttpResponse()
>>>>>>> 93012f740efc69a9841645c1062564e88025181a

            #for treeMenu
            to_text = spec_param_json.replace('param_name', 'text')
            items = to_text.replace('children_spec', 'items')

<<<<<<< HEAD
            #with open('./web_site/media/tree_menu.json', 'w') as f: f.write(items)
            #with open('./web_site/media/spec_param_list.json', 'w') as f: f.write(spec_param_json)
            #print items
            json_params['params_list'] = json.loads(items)
            json_params['connected_type'] = raw_spec.get('connected_type', None)
            json_params['connecting_type'] = raw_spec.get('connecting_type', None)
            json_params['spec_param_list'] = json.loads(spec_param_json)
            #print json_params
            return HttpResponse(json.dumps(json_params), mimetype="application/json")
            #return HttpResponse()

    def get_spec(self, request):
        """get specification for edit
        """
=======
#            with open('./web_blik/media/tree_menu.json', 'w') as f: f.write(items)
            with open(os.path.join(settings.MEDIA_ROOT, "tree_menu.json"), "w") as f:
                f.write(items)
#            with open('./web_blik/media/spec_param_list.json', 'w') as f: f.write(spec_param_json)
            with open(os.path.join(settings.MEDIA_ROOT, "spec_param_list.json"), "w") as f:
                f.write(spec_param_json)

            return HttpResponse()

    def get_spec(self, request):
        """Get specification for edit"""
        connion_type = conned_type = allowed_types = ''

>>>>>>> 93012f740efc69a9841645c1062564e88025181a
        spec_id = request.GET.get('spec_id',)
        load_page = request.META.get('PATH_INFO')
        render_page = load_page.split('/')
        #render specification page
        if spec_id:
            raw_spec = self.specification.getSpecification(spec_id).to_dict()
            return render_to_response(render_page[1]+'.html', {'spec_id': raw_spec['_id']})

        #render page for create
        items_list = self._search_spec(SPEC_TYPE[render_page[1]])
        return render_to_response(render_page[1]+'_create.html', { 'items_list': items_list})

    def get_specification_params(self, request):
        """ implement GET method """
        if request.GET.get('spec_id', None):
            raw_spec = self.specification.getSpecification(request.GET['spec_id']).to_dict()
            spec_param_json = json.dumps(raw_spec['params_spec'])

            #for treeMenu
<<<<<<< HEAD
            to_text = spec_param_json.replace('param_name','text')
            items = to_text.replace('children_spec','items')

            json_data = {'spec_info': raw_spec,
                         'items': json.loads(items)}

            return HttpResponse(json.dumps(json_data), mimetype="application/json")
        return HttpResponse()

    def search_del(self,request):
        """searching and delete for all specifications
        """
        #if request.GET and not request.POST:
=======
            to_text = spec_param_json.replace('param_name', 'text')
            items = to_text.replace('children_spec', 'items')

            return render_to_response(render_page[1] + '.html', {'spec_id': raw_spec['_id'],
                                                                 'spec_name': raw_spec['type_name'],
                                                                 'spec_desc': raw_spec['description'],
                                                                 'parent_spec': raw_spec['parent_type_name'],
                                                                 'connion_type': connion_type,
                                                                 'conned_type': conned_type,

                                                                 # init()
                                                                 'spec_param_list': json.dumps(raw_spec),
                                                                 'items': items,
                                                                 'type': 'specification', # TODO modify init()
                                                                 'res_param_dict': {},
                                                                 'allowed_coll': {},
                                                                 'assigned_coll': {}},
                                      context_instance=RequestContext(request))

        #render page for create
        items_list = self._search_spec(SPEC_TYPE[render_page[1]])

        return render_to_response(render_page[1] + '.html', {'items_list': items_list},
                                  context_instance=RequestContext(request))

    def search_del(self, request):
        """Searching and delete for all specifications"""
>>>>>>> 93012f740efc69a9841645c1062564e88025181a
        search_spec_name = request.GET.get('s',)
        search_spec_type = request.GET.get('spec_type',)
        search_page = request.META.get('PATH_INFO').split('/')
        del_item_id = request.POST.get('del_id',)

        spec_type = [key for key, value in SEARCH_PAGE.iteritems() if value == search_page[1]][0]
        spec_page = [key for key, value in SPEC_TYPE.iteritems() if value == spec_type][0]

        allowed_types = ''
        #render search spec page with data
        if search_spec_type:
            if del_item_id:
                self.specification.deleteSpecification(del_item_id)

            spec_list = self._search_spec(search_spec_type, search_spec_name)
            #print search_spec_type, spec_list
            if search_spec_type == ELEM_TYPES['IS_COLL'] and spec_list:
                #print 'spec_list', spec_list
                allowed_types = json.dumps(spec_list[0]['allowed_types'])

<<<<<<< HEAD
            #print 'allowed_types',allowed_types, SEARCH_PAGE[search_spec_type]
            return render_to_response(SEARCH_PAGE[search_spec_type]+'.html', {'spec_list': spec_list,
                                                                              'allowed_types': allowed_types,
                                                                              'spec_type': spec_type,
                                                                              'spec_page': spec_page})
=======
            return render_to_response(SEARCH_PAGE[search_spec_type] + '.html', {'spec_list': spec_list,
                                                                                'allowed_types': allowed_types,
                                                                                'spec_type': spec_type,
                                                                                'spec_page': spec_page},
                                      context_instance=RequestContext(request))
>>>>>>> 93012f740efc69a9841645c1062564e88025181a
        # render empty page
        return render_to_response(search_page[1] + '.html', {'spec_type': spec_type,
                                                             'spec_page': spec_page},
                                  context_instance=RequestContext(request))

    def _search_spec(self, spec_type, spec_name=None):
        if not spec_name:
            self.spec_filter = {'spec_type': spec_type}
        else:
            self.spec_filter = {'type_name': spec_name,
                                'spec_type': spec_type}

        res_list = self.specification.findSpecification(spec_type, self.spec_filter)
        spec_list = []
        #convert spec id for @name.id in .html
        if res_list:
            for item in res_list:
                s = item.to_dict()
                s['id'] = s.pop('_id')
                spec_list.append(s)

        return spec_list

    def update_elem(self, type_spec):
        """Update elements by specification
        {$rename: { <old name1>: <new name1>, <old name2>: <new name2>, ... } }
        """
        pass