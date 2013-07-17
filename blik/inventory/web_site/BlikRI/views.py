#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" implemented all API """

import json
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext

from blik.inventory.api.management_api import ManagementAPI
from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
from blik.inventory.api.collection_oper_api import CollectionOperationalAPI
from blik.inventory.api.connection_oper_api import ConnectionOperationalAPI, CONNECTED, CONNECTING
from blik.inventory.core.base_entities import *
from resource_api import ResourceAPI
from collection_api import CollectionAPI
from connection_api import ConnectionAPI

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
    """ Base class API """
    def __init__(self):
        self.specification = ManagementAPI()
        #self.resource = ResourceOperationalAPI()
        #self.collection = CollectionOperationalAPI()

    def conn_search_del(self, request):
        """ Search and delete connections """
        conn = ConnectionAPI()
        conn_list = []
        if request.GET and not request.POST:
            conn_list = conn.search(request.GET)
        elif request.POST:
            conn_list = conn.delete(request.POST.get('del_id', None), request.GET)

        return render_to_response('connection_search.html',
                                  {'res_list': conn_list, 'elem_type': ELEM_TYPES['IS_CONN']},
                                  context_instance=RequestContext(request))

    def connection(self, request):
        """ Get connection for create/modify """
        conn_id = request.GET.get('elem_id',)
        if conn_id:
            return render_to_response('connection.html', { 'conn_id': conn_id,})

        # create connection
        conn_spec_list = self._search_spec(ELEM_TYPES['IS_CONN'])
        return  render_to_response('connection_create.html',
                                   {'items_list': conn_spec_list},
                                   context_instance=RequestContext(request))

    def get_connection_params(self, request):
        """ Implement GET method """
        if request.GET.get('spec_id', None):
            connection = ConnectionOperationalAPI()
            conn_info = connection.getConnectionInfo(request.GET['spec_id']).to_dict()
            conn_spec = self._search_spec(ELEM_TYPES['IS_CONN'], conn_info['specification_name'])[0]

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

        return HttpResponse()

    def coll_search_del(self, request):
        """ Search and delete collections """
        coll = CollectionAPI()
        coll_list = []
        if request.GET and not request.POST:
            coll_list = coll.search(request.GET)
        elif request.POST:
            coll_list = coll.delete(request.POST.get('del_id', None), request.GET)
        return render_to_response('collection_search.html',
                                  {'res_list': coll_list,'elem_type': ELEM_TYPES['IS_COLL']},
                                  context_instance=RequestContext(request))

    def collection(self, request):
        """ Get collection for modify """
        if request.GET.get('elem_id', None):
            return render_to_response('collection.html',
                                      {'coll_id': request.GET['elem_id']},
                                      context_instance=RequestContext(request))

        coll_spec_list = self._search_spec(ELEM_TYPES['IS_COLL'])
        return  render_to_response('collection_create.html',
                                   {'items_list': coll_spec_list},
                                   context_instance=RequestContext(request))

    def get_collection_params(self, request):
        """ Implement GET method """
        if request.GET.get('coll_id', None):
            collection = CollectionOperationalAPI()

            coll_info = collection.getCollectionInfo(request.GET['coll_id']).to_dict()
            coll_spec = self._search_spec(ELEM_TYPES['IS_COLL'], coll_info['specification_name'])[0]

            # for TreeMenu
            spec_params_json = json.dumps(coll_spec['params_spec'])
            to_text = spec_params_json.replace('param_name','text')
            items = to_text.replace('children_spec','items')

            json_data = {'coll_spec': coll_spec['params_spec'],
                         'coll_info': coll_info,
                         'allowed_types': coll_spec['allowed_types'],
                         'items': json.loads(items)}
            return HttpResponse(json.dumps(json_data), mimetype="application/json")

        return HttpResponse()

    def resource(self,request):
        """ Render resource page for creating and modifying """
        # get resource for modify
        if request.GET.get('elem_id', None):
            # get connections list
            connection = ConnectionAPI()
            conn_list_raw = connection.search()
            conn_list = []
            if conn_list_raw:
                for conn in conn_list_raw:
                    conn_list.append(conn['specification_name'])

            return render_to_response('resource.html',
                                      {'res_id': request.GET['elem_id'], 'conn_list': list(set(conn_list))},
                                      context_instance=RequestContext(request))

        # get specs for creating resource
        res_spec_list = self._search_spec(ELEM_TYPES['IS_RES'])
        return render_to_response('resource_create.html',
                                  {'items_list': res_spec_list},
                                  context_instance=RequestContext(request))

    def get_resource_params(self, request):
        """ Implement GET method for get resource info """
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

            # find created collections
            collection  = CollectionOperationalAPI()
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
            to_text = spec_params_json.replace('param_name','text')
            items = to_text.replace('children_spec','items')

            json_data = {'res_spec': res_spec['params_spec'],
                         'res_info': res_info,
                         'items': json.loads(items),
                         'allowed_coll': allow_coll_list,
                         'assigned_coll': assigned_coll_list}

            return HttpResponse(json.dumps(json_data), mimetype="application/json")

        return HttpResponse()

    def res_search_del(self, request):
        """ Searching and deleting resource """
        res = ResourceAPI()
        if request.GET and not request.POST:

            res_list = res.search_resource(request.GET)
            #json_data = {'res_list': res_list, 'elem_type': ELEM_TYPES['IS_RES']}
            #return HttpResponse(json.dumps(json_data), mimetype="application/json")

            return render_to_response('resource_search.html',
                                      {'res_list': res_list, 'elem_type': ELEM_TYPES['IS_RES']},
                                      context_instance=RequestContext(request))
        elif request.POST:
            res_list = res.del_resource(request.POST.get('del_id',), request.GET)
            return render_to_response('resource_search.html',
                                      {'res_list': res_list, 'elem_type': ELEM_TYPES['IS_RES']},
                                      context_instance=RequestContext(request))

        # render empty page
        return render_to_response('resource_search.html',
                                  {'res_list': [], 'elem_type': ELEM_TYPES['IS_RES']},
                                  context_instance=RequestContext(request))

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

            conn_spec = self._search_spec(ELEM_TYPES['IS_CONN'], elem_type)[0]
            Connection.setup_specification([ConnectionSpecification(conn_spec)])

            if elem_id:
                connection.updateConnection(elem_id, elem_desc, connecting_res_id, connected_res_id,
                                            additional_parameters=json.loads(raw_param_res))
            else:
                connection.connectResources(elem_type, connecting_res_id, connected_res_id, elem_desc,
                                            **json.loads(raw_param_res))

            return HttpResponse()

    def _update_collections(self, old_assigned_to_coll, new_assigned_to_coll, res_id):
        """ Append or remove resource from collections """
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

    def save_spec(self,request):
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

    def get_connection_by_type(self, request):
        """ Get connection type for resource """
        if request.is_ajax():
            res_id = request.GET.get('elem_id', None)
            conn_type = request.GET.get('conn_id', None)

            connection = ConnectionOperationalAPI()
            resource = ResourceOperationalAPI()
            connected_res = connection.getLinkedResources(res_id, conn_type=conn_type, conn_direction=CONNECTED)
            connecting_res = connection.getLinkedResources(res_id, conn_type=conn_type, conn_direction=CONNECTING)

            connected_list = []
            for tt in connecting_res:
                conn_res_id = tt.to_dict()['connected_resource']
                res_info = resource.getResourceInfo(conn_res_id).to_dict()
                connected_list.append(res_info['specification_name'])

            connecting_list = []
            for tt in connected_res:
                conn_res_id = tt.to_dict()['connecting_resource']
                res_info = resource.getResourceInfo(conn_res_id).to_dict()
                connecting_list.append(res_info['specification_name'])
            return HttpResponse(json.dumps({'connecting_list': connecting_list,
                                            'connected_list': connected_list}), mimetype="application/json")

    def get_param_spec(self,request):
        if request.is_ajax():
            spec_id = request.GET.get('spec_id',)
            raw_spec = self.specification.getSpecification(spec_id).to_dict()

            json_params = {}
            # for connections
            if raw_spec['spec_type'] == ELEM_TYPES['IS_CONN']:
                connected_type = raw_spec['connected_type']
                connecting_type = raw_spec['connecting_type']
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
                    json_params['connecting_res_list'] = connecting_res_list

                res_filter = {'specification_name': str(connected_type)}
                raw_connected_res_list = self._search_elem(res_filter, resource)
                if raw_connected_res_list:
                    connected_res_list = []
                    for res in raw_connected_res_list:
                        connected_res_dict = dict()
                        connected_res_dict['connected_res_id'] = res['id']
                        connected_res_dict['res_name'] = res['specification_name']
                        connected_res_list.append(connected_res_dict)
                    json_params['connected_res_list'] = connected_res_list

                    # for create specifications
            load_page =  request.META.get('HTTP_REFERER').split('/')
            spec_param_json = json.dumps(raw_spec)
            if load_page[3] in SPEC_TYPE.keys():
                to_text = spec_param_json.replace('param_name','text')
                items = to_text.replace('children_spec','items')

                json_params = {'spec_param_list': json.loads(spec_param_json), 'params_list': json.loads(items)}
                return HttpResponse(json.dumps(json_params), mimetype="application/json")

            #for treeMenu
            to_text = spec_param_json.replace('param_name','text')
            items = to_text.replace('children_spec','items')

            json_params['params_list'] = json.loads(items)
            json_params['connected_type'] = raw_spec.get('connected_type', None)
            json_params['connecting_type'] = raw_spec.get('connecting_type', None)
            json_params['spec_param_list'] = json.loads(spec_param_json)
            return HttpResponse(json.dumps(json_params), mimetype="application/json")

    def get_spec(self, request):
        """ Get specification for edit """
        spec_id = request.GET.get('spec_id',)
        load_page = request.META.get('PATH_INFO')
        render_page = load_page.split('/')
        #render specification page
        if spec_id:
            raw_spec = self.specification.getSpecification(spec_id).to_dict()
            return render_to_response(render_page[1] + '.html',
                                      {'spec_id': raw_spec['_id']},
                                      context_instance=RequestContext(request))

        #render page for create
        items_list = self._search_spec(SPEC_TYPE[render_page[1]])
        return render_to_response(render_page[1] + '_create.html',
                                  {'items_list': items_list},
                                  context_instance=RequestContext(request))

    def get_specification_params(self, request):
        """ Implement GET method """
        if request.GET.get('spec_id', None):
            raw_spec = self.specification.getSpecification(request.GET['spec_id']).to_dict()
            spec_param_json = json.dumps(raw_spec['params_spec'])

            #for treeMenu
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
            if search_spec_type == ELEM_TYPES['IS_COLL'] and spec_list:
                allowed_types = json.dumps(spec_list[0]['allowed_types'])

            return render_to_response(SEARCH_PAGE[search_spec_type] + '.html',
                                      {'spec_list': spec_list,
                                       'allowed_types': allowed_types,
                                       'spec_type': spec_type,
                                       'spec_page': spec_page},
                                      context_instance=RequestContext(request))
            # render empty page
        return render_to_response(search_page[1] + '.html',
                                  {'spec_type': spec_type, 'spec_page': spec_page},
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
        """update elements by specification
        {$rename: { <old name1>: <new name1>, <old name2>: <new name2>, ... } }
        """

        pass
