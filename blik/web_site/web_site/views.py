# -*- coding: utf-8 -*-

from blik.inventory.api.management_api import ManagementAPI
from blik.inventory.backend.common import  CommonDatabaseAPI
from django.shortcuts import render_to_response
from django.http import Http404
from django.http import HttpResponseRedirect
import json
import ast

class SetViews():
    def __init__(self):
        self.specification = ManagementAPI()

    def resource(self,request):

        return render_to_response('search_spec_res.html')

    def collection(self,request):

        return render_to_response()

    def create(self,request):
        spec_name = request.POST.get('spec_name',)
        description = request.POST.get('spec_desc',)
        spec_parent = request.POST.get('parent_spec',)
        raw_param_spec = request.POST.get('param_spec',)
        list_param_spec = []

        if raw_param_spec != None and raw_param_spec != 'null':
            spec = ast.literal_eval(raw_param_spec)

            if isinstance(spec, tuple):
                i=0
                while i<len(spec):
                    list_param_spec.append(spec[i])
                    i += 1
            elif isinstance(spec, dict):
                list_param_spec.append(spec)

        if spec_name != None:
            if self.specification.createSpecification(spec_name, spec_parent, 'resource', description, params_spec=list_param_spec) != None:
                return HttpResponseRedirect('/create_spec_res/')

        return render_to_response('create_spec_res.html')

    def search(self,request):
        self.spec_name = request.GET.get('s',)
        self.del_item_id = request.POST.get('del_id',)

        if self.spec_name == '':    
            return render_to_response('search_spec_res.html', {'error': True})


        if self.del_item_id == None:
            spec_list = self._search_item(self.spec_name)

            return render_to_response('search_spec_res.html', {'spec_list': spec_list})
        else:
            self._delete_item(self.del_item_id )
            spec_list = self._search_item(self.spec_name)

            return render_to_response('search_spec_res.html', {'spec_list': spec_list})

        return render_to_response('search_spec_res.html', {'spec_list': spec_list})

    def modal(self,request):

        return render_to_response('modal_spec_res.html')


    def edit(self,request):
        spec_id = request.GET.keys()

        spec_name = request.POST.get('spec_name',)
        description = request.POST.get('spec_desc',)
        spec_parent = request.POST.get('parent_spec',)
        raw_param_spec = request.POST.get('param_spec',)
        list_param_spec = []

        if raw_param_spec != None and raw_param_spec != 'null':
            spec = ast.literal_eval(raw_param_spec)

            if isinstance(spec, tuple):
                i=0
                while i<len(spec):
                    list_param_spec.append(spec[i])
                    i += 1
            elif isinstance(spec, dict):
                list_param_spec.append(spec)


        if spec_name != None: 
            if self.specification.updateSpecification(spec_id[0], spec_name, spec_parent, 'resource', description, params_spec=list_param_spec) != None:
                return HttpResponseRedirect('/search_spec_res/')



        raw_spec = self.specification.getSpecification(spec_id[0]).to_dict()
        return render_to_response('edit_spec_res.html', {'spec_name': raw_spec['type_name'],
                                                         'spec_desc': raw_spec['description'],
                                                         'parent_spec': raw_spec['parent_type_name'],
                                                         'spec_param_list': raw_spec['params_spec'],
                                                           })

    def _delete_item(self,item_id):
        self.specification.deleteSpecification(item_id)

    def _search_item(self,spec_name):
        self.spec_filter = {'type_name': spec_name}
        self.res_list = self.specification.findSpecification(CommonDatabaseAPI.ET_RESOURCE, self.spec_filter)
        spec_list = []

        for item in self.res_list:
            s = item.to_dict()
            spec_list.append(s)
            s['id'] = s.pop('_id')

        return spec_list