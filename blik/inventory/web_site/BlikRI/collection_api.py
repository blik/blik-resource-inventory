# -*- coding: utf-8 -*-
__author__ = 'yac'
from blik.inventory.api.collection_oper_api import CollectionOperationalAPI
from blik.inventory.api.management_api import ManagementAPI

class CollectionAPI(object):
    def search(self, params_dict):
        collection = CollectionOperationalAPI()
        resource_filter = {}
        for param, val in params_dict.iteritems():
            if param == 'specification_name' and val:
                resource_filter[param] = val

        specification = ManagementAPI()

        res_list = self._search_elem(resource_filter, collection)

        coll_list = []
        if res_list:
            for param in res_list:
                spec = specification.findSpecification('collection', {'type_name': param['specification_name']})
                for item in spec:
                    d = item.to_dict()
                    param['allowed_types'] = d['allowed_types']
                    coll_list.append(param)

        return coll_list

    def delete(self, resource_id, params):
        resource = CollectionOperationalAPI()
        resource.deleteCollection(resource_id)

        return self.search(params)

    def _search_elem(self, resource_filter, element):
        obj_list = []
        if isinstance(element, CollectionOperationalAPI):
            obj_list = element.findCollections(resource_filter)

        elems_list = []
        for item in obj_list:
            s = item.to_dict()
            s['id'] = s.pop('_id')
            elems_list.append(s)

        return elems_list
