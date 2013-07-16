# -*- coding: utf-8 -*-
__author__ = 'yac'
from blik.inventory.api.management_api import ManagementAPI

class SpecificationAPI(object):
    def search(self, params):
        spec = ManagementAPI()
        search_spec_name = params.get('s',)
        search_spec_type = params.get('spec_type',)

        resource_filter = {}
        #if res_name:
        #    resource_filter['specification_name'] = res_name
        #elif res_status:
        #    resource_filter['resource_status'] = res_status
        #elif res_ext_sys:
        #    resource_filter['external_system'] = res_ext_sys

        return self._search_elem(resource_filter, resource)

    def delete(self, resource_id, params):
        resource = ManagementAPI()
        resource.removeResource(resource_id)

        return self.search_resource(params)

    def _search_elem(self, resource_filter, element):
        obj_list = []
        if isinstance(element, ResourceOperationalAPI):
            obj_list = element.findResources(resource_filter)
            #elif isinstance(element, CollectionOperationalAPI):
        #    obj_list = element.findCollections(resource_filter)
        #elif isinstance(element, ConnectionOperationalAPI):
        #    obj_list = element.findConnection(resource_filter)

        elems_list = []
        for item in obj_list:
            s = item.to_dict()
            s['id'] = s.pop('_id')
            elems_list.append(s)

        return elems_list
