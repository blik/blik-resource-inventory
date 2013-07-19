# -*- coding: utf-8 -*-
__author__ = 'yac'
from blik.inventory.api.management_api import ManagementAPI
from blik.inventory.api.connection_oper_api import ConnectionOperationalAPI
from blik.inventory.api.resource_oper_api import ResourceOperationalAPI

class ConnectionAPI(object):
    def search(self, params_dict=None):
        conn = ConnectionOperationalAPI()
        resource_filter = {}
        if params_dict:
            #print '>>>>>>>>>>>>',params_dict
            for param, val in params_dict.iteritems():
                if param == 'specification_name' and val:
                    resource_filter[param] = val
        return self._search_elem(resource_filter, conn)

    def delete(self, resource_id, params):
        resource = ConnectionOperationalAPI()
        resource.deleteConnection(resource_id)

        return self.search(params)

    def _search_elem(self, resource_filter, element):
        obj_list = []
        if isinstance(element, ConnectionOperationalAPI):
            obj_list = element.findConnection(resource_filter)

        resource = ResourceOperationalAPI()
        specification = ManagementAPI()

        elems_list = []
        for item in obj_list:
            s = item.to_dict()
            #print s
            spec = specification.findSpecification('connection', {'type_name': s['specification_name']})[0].to_dict()
            s['id'] = s.pop('_id')
            s['connected_res_name'] = resource.getResourceInfo(s['connected_resource']).to_dict()['resource_name']
            s['connecting_res_name'] = resource.getResourceInfo(s['connecting_resource']).to_dict()['resource_name']
            s['connecting_type'] = spec['connecting_type']
            s['connected_type'] = spec['connected_type']

            elems_list.append(s)
        #print elems_list
        return elems_list
