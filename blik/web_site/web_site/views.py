# -*- coding: utf-8 -*-

from blik.inventory.api.management_api import ManagementAPI
from blik.inventory.backend.common import  CommonDatabaseAPI
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect

import ast

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

    def modal(self,request):

        return render_to_response('modal_spec_res.html', {'spec_name':'name'})

    def create_update(self, request):
        connion_type = conned_type = allowed_types = ''
        list_param_spec = []

        spec_name = request.POST.get('spec_name',)
        spec_type = request.POST.get('spec_type',)
        description = request.POST.get('spec_desc',)
        spec_parent = request.POST.get('parent_spec',)
        connion_type = request.POST.get('connion_type',)
        conned_type = request.POST.get('conned_type',)
        allowed_types = request.POST.get('allowed_types',)
        raw_param_spec = request.POST.get('param_spec',)
        spec_id = request.GET.get('spec_id',)

        load_page = request.META.get('PATH_INFO')
        render_page = load_page.split('/')

        if raw_param_spec != None and raw_param_spec != 'null':
            spec = ast.literal_eval(raw_param_spec)
            if isinstance(spec, tuple):
                i=0
                while i<len(spec):
                    list_param_spec.append(spec[i])
                    i += 1
            elif isinstance(spec, dict):
                list_param_spec.append(spec)

        if request.POST != {} and request.GET == {}:
            if spec_type == 'resource':
                if self.specification.createSpecification(spec_name, spec_parent, spec_type, description, params_spec=list_param_spec) != None:
                    return HttpResponseRedirect(load_page)
            elif spec_type == 'connection':
                if self.specification.createSpecification(spec_name, spec_parent, spec_type, description, connecting_type=connion_type, connected_type=conned_type, params_spec=list_param_spec) != None:
                    return HttpResponseRedirect(load_page)
            elif spec_type == 'collection':
                if self.specification.createSpecification(spec_name, spec_parent, spec_type, description, allowed_types=allowed_types, params_spec=list_param_spec) != None:
                    return HttpResponseRedirect(load_page)                

        elif spec_id != None and spec_name != None  and request.POST != {}:
            if spec_type == 'resource':
                if self.specification.updateSpecification(spec_id, spec_name, spec_parent, spec_type, description, params_spec=list_param_spec) != None:
                    return HttpResponseRedirect('/'+SEARCH_PAGE[spec_type]+'/')
            elif spec_type == 'connection':
                if self.specification.updateSpecification(spec_id, spec_name, spec_parent, spec_type, description, connecting_type=connion_type, connected_type=conned_type, params_spec=list_param_spec) != None:
                    return HttpResponseRedirect('/'+SEARCH_PAGE[spec_type]+'/')
            elif spec_type == 'collection':
                if self.specification.updateSpecification(spec_id, spec_name, spec_parent, spec_type, description, allowed_types=allowed_types, params_spec=list_param_spec) != None:
                    return HttpResponseRedirect('/'+SEARCH_PAGE[spec_type]+'/')

        elif spec_id != None and request.POST == {}:
            raw_spec = self.specification.getSpecification(spec_id).to_dict()

            if SPEC_TYPE[render_page[1]] == 'connection':
                connion_type = raw_spec['connecting_type']
                conned_type = raw_spec['connected_type']

            elif SPEC_TYPE[render_page[1]] == 'collection':
                allowed_types = raw_spec['allowed_types']
   
            return render_to_response(render_page[1]+'.html', {'spec_name': raw_spec['type_name'],
                                                         'spec_desc': raw_spec['description'],
                                                         'parent_spec': raw_spec['parent_type_name'],
                                                         'connion_type': connion_type,
                                                         'conned_type': conned_type,
                                                         'allowed_types': allowed_types,
                                                         'spec_param_list': raw_spec['params_spec']})

        
        return render_to_response(render_page[1]+'.html')

    def search_del(self,request):
        search_spec_name = request.GET.get('s',)
        search_spec_type = request.GET.get('spec_type',)
        search_page = request.META.get('PATH_INFO').split('/')

        del_item_id = request.POST.get('del_id',)

        if request.GET != {} and request.POST == {}:
            spec_list = self._search_item(search_spec_name, search_spec_type)
            if spec_list == []:
                return render_to_response(SEARCH_PAGE[search_spec_type]+'.html', {'search_spec_name': search_spec_name})
            else:
                return render_to_response(SEARCH_PAGE[search_spec_type]+'.html', {'spec_list': spec_list})

        elif del_item_id != None:
            self._delete_item(del_item_id )
            spec_list = self._search_item(search_spec_name, search_spec_type)

            return render_to_response(SEARCH_PAGE[search_spec_type]+'.html', {'spec_list': spec_list})
            
        return render_to_response(search_page[1]+'.html')#,{'spec_type': SPEC_TYPE[search_page[1]]})

    def _delete_item(self,item_id):
        self.specification.deleteSpecification(item_id)

    def _search_item(self,spec_name,spec_type):
        self.spec_filter = {'type_name': spec_name}
        self.res_list = self.specification.findSpecification(spec_type, self.spec_filter)
        spec_list = []

        for item in self.res_list:
            s = item.to_dict()
            s['id'] = s.pop('_id')
            spec_list.append(s)
            
        return spec_list