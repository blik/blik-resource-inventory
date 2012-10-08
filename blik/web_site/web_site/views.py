# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from blik.inventory.api.management_api import ManagementAPI
from blik.inventory.backend.common import  CommonDatabaseAPI
import json
from django.http import Http404
import ast
from django.http import HttpResponseRedirect

#from django.template import Context

#from django.http import HttpResponse


class SetViews():
    def __init__(self):
        self.specification = ManagementAPI()

    def resource(self,request):

        return render_to_response('search_spec_res.html')

    def collection(self,request):

        return render_to_response()

    def create(self,request):
        spec_name = request.POST.get('spec_name',)
        description = request.POST.get('description',)
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
        self.get_item_id = request.POST.get('item_id',)
        spec_list = []

        self.raw_spec = self.specification.getSpecification(self.get_item_id)
        for item in self.raw_spec:
            s = item.to_dict()
            spec_list.append(s)

        return render_to_response('modal_spec_res.html',{'spec_list': spec_list})

    def _delete_item(self,item_id):
        self.item = item_id.encode('ascii','ignore')
        print type(self.item)
        #self.item = ast.literal_eval(item_id)
        self.specification.deleteSpecification(self.item)

    def _search_item(self,spec_name):
        self.spec_filter = {'type_name': spec_name}
        self.res_list = self.specification.findSpecification(CommonDatabaseAPI.ET_RESOURCE, self.spec_filter)
        spec_list = []

        for item in self.res_list:
            s = item.to_dict()
            spec_list.append(s)
            s['id'] = s.pop('_id')

        return spec_list