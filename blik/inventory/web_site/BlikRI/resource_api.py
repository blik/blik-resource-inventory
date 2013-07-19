# -*- coding: utf-8 -*-
__author__ = 'yac'
from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
import json

class ResourceAPI(object):
    def search_resource(self, params_dict):
        resource = ResourceOperationalAPI()

        resource_filter = {}
        for param, val in params_dict.iteritems():
            if val:
                resource_filter[param] = val

        return self._search_elem(resource_filter, resource)

    def del_resource(self, resource_id, params):
        resource = ResourceOperationalAPI()
        resource.removeResource(resource_id)

        return self.search_resource(params)

    def _search_elem(self, resource_filter, element):
        obj_list = []
        if isinstance(element, ResourceOperationalAPI):
            obj_list = element.findResources(resource_filter)


        elems_list = []
        for item in obj_list:
            s = item.to_dict()
            s['id'] = s.pop('_id')
            elems_list.append(s)

        return elems_list