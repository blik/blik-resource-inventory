# -*- coding: utf-8 -*-

from blik.inventory.api.management_api import ManagementAPI
from blik.inventory.backend.common import  CommonDatabaseAPI
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils import simplejson

import ast
import json

SEARCH_PAGE = {'resource': 'spec_search_res',
               'connection': 'spec_search_conn',
               'collection': 'spec_search_coll'}

SPEC_TYPE = {'specification_res': 'resource',
             'specification_conn': 'connection',
             'specification_coll': 'collection'} 

class SetViews():
    def __init__(self):
        self.specification = ManagementAPI()

    def resource(self,request):

        return render_to_response('spec_search_res.html')

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


            params_spec = ast.literal_eval(raw_param_spec)

            if spec_id != '':
                print 'update'
                if spec_type == 'resource':
                    self.specification.updateSpecification(spec_id, spec_name, spec_parent, spec_type, description, params_spec=params_spec)
                elif spec_type == 'connection':
                    self.specification.updateSpecification(spec_id, spec_name, spec_parent, spec_type, description, connecting_type=connion_type, connected_type=conned_type, params_spec=params_spec)
                elif spec_type == 'collection':
                    self.specification.updateSpecification(spec_id, spec_name, spec_parent, spec_type, description, allowed_types=allowed_types, params_spec=params_spec)

            if spec_id == '':
                print 'save'
                if spec_type == 'resource':
                    spec = self.specification.createSpecification(spec_name, spec_parent, spec_type, description, params_spec=params_spec).to_dict()
                    #self.SPEC_ID = spec['_id']
                    #self.SPEC_NAME = spec['type_name']
                elif spec_type == 'connection':
                    self.specification.createSpecification(spec_name, spec_parent, spec_type, description, connecting_type=connion_type, connected_type=conned_type, params_spec=params_spec)
                elif spec_type == 'collection':
                    self.specification.createSpecification(spec_name, spec_parent, spec_type, description, allowed_types=allowed_types, params_spec=params_spec)
            
            return HttpResponse()

    def modal(self,request):
        cookies = request.META.get('HTTP_COOKIE')
        spec_id = request.COOKIES['spec_id']

        raw_spec = self.specification.getSpecification(spec_id).to_dict()
        spec_param_json = json.dumps(raw_spec['params_spec'])

        to_text = spec_param_json.replace('param_name','text')
        items = to_text.replace('children_spec','items')

        return render_to_response('modal_spec_res.html', {'items': items})

    def param_spec(self,request):
        spec_id = request.GET.get('spec_id',)

        #clear data in file
        open('./web_site/media/tree_menu.json', 'w').close()
        open('./web_site/media/spec_param_list.json', 'w').close()

        if request.is_ajax():
            spec_id = request.GET.get('spec_id',)

            raw_spec = self.specification.getSpecification(spec_id).to_dict()
            spec_param_json = json.dumps(raw_spec['params_spec'])
            #for treeMenu

            to_text = spec_param_json.replace('param_name','text')
            items = to_text.replace('children_spec','items') 
            f = open('./web_site/media/tree_menu.json', 'w')
            f.write(items)
            f.closed
            f = open('./web_site/media/spec_param_list.json', 'w')
            f.write(spec_param_json)
            f.closed
            return HttpResponse()

    def get_spec(self, request):
        connion_type = conned_type = allowed_types = ''

        spec_id = request.GET.get('spec_id',)
        load_page = request.META.get('PATH_INFO')
        render_page = load_page.split('/')

#render specification page
        if spec_id:
            raw_spec = self.specification.getSpecification(spec_id).to_dict()

            if SPEC_TYPE[render_page[1]] == 'connection':
                connion_type = raw_spec['connecting_type']
                conned_type = raw_spec['connected_type']
            elif SPEC_TYPE[render_page[1]] == 'collection':
                allowed_types = raw_spec['allowed_types']

            spec_param_json = json.dumps(raw_spec['params_spec'])
            #for treeMenu
            to_text = spec_param_json.replace('param_name','text')
            items = to_text.replace('children_spec','items')

            return render_to_response(render_page[1]+'.html', {'spec_id': raw_spec['_id'],
                                                               'spec_name': raw_spec['type_name'],
                                                               'spec_desc': raw_spec['description'],
                                                               'parent_spec': raw_spec['parent_type_name'],
                                                               'connion_type': connion_type,
                                                               'conned_type': conned_type,
                                                               'allowed_types': allowed_types,
                                                               'spec_param_list': spec_param_json, 
                                                               'items': items})
        #render page for create
        items_list = self._search_item(SPEC_TYPE[render_page[1]])

        return render_to_response(render_page[1]+'.html', { 'items_list': items_list})

    def search_del(self,request):
        search_spec_name = request.GET.get('s',)
        search_spec_type = request.GET.get('spec_type',)
        search_page = request.META.get('PATH_INFO').split('/')
        del_item_id = request.POST.get('del_id',)

        spec_type = [key for key, value in SEARCH_PAGE.iteritems() if value == search_page[1]][0]
        spec_page = [key for key, value in SPEC_TYPE.iteritems() if value == spec_type][0]

        #render search spec page with data
        if request.GET != {} and request.POST == {}:
            #print '1'
            spec_list = self._search_item(search_spec_type, search_spec_name)
            #if spec_list == []:
                #return @spec_name when didn't found
            #    return render_to_response(SEARCH_PAGE[search_spec_type]+'.html', {'search_spec_name': search_spec_name})
            #else:

            return render_to_response(SEARCH_PAGE[search_spec_type]+'.html', {'spec_list': spec_list,
                                                                               'spec_type': spec_type,
                                                                               'spec_page': spec_page})
        #del spec
        elif del_item_id != None:
            self.specification.deleteSpecification(del_item_id)
            spec_list = self._search_item(search_spec_type, search_spec_name)

            return render_to_response(SEARCH_PAGE[search_spec_type]+'.html', {'spec_list': spec_list,
                                                                               'spec_type': spec_type,
                                                                               'spec_page': spec_page})

        #render empty search spec
        return render_to_response(search_page[1]+'.html', {'spec_type': spec_type,
                                                           'spec_page': spec_page})

    def _search_item(self, spec_type, spec_name=None):
        if spec_name == None:
            self.spec_filter = {'spec_type': spec_type}
        else:
            self.spec_filter = {'type_name': spec_name,
                                'spec_type': spec_type}

        self.res_list = self.specification.findSpecification(spec_type, self.spec_filter)
        spec_list = []
        #convert spec id for @name.id in .html
        for item in self.res_list:
            s = item.to_dict()
            s['id'] = s.pop('_id')
            spec_list.append(s)
            
        return spec_list