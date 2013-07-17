#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Purpose: Blik Inventory API for Connection
Created: 20.09.2012
Author: Yaroslav Chernyakov
"""

from blik.inventory.backend.common import CommonDatabaseAPI
from blik.inventory.utils.ri_spec_manager import InventoryConfiguration
from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
from blik.inventory.api.management_api import ManagementAPI
from blik.inventory.core.inv_exceptions import BIException
from blik.inventory.core.base_entities import *

BOTH = ['connecting_resource', 'connected_resource']
CONNECTING = 'connecting_resource'
CONNECTED = 'connected_resource'
CONFIG_FILE = "/opt/blik/inventory/conf/blik-ri-conf.yaml"

class ConnectionOperationalAPI():
    """ Implemented API for connection """
    def __init__(self):
        self.conf = InventoryConfiguration()
        self.db_conn = self.conf.get_backend_db(CONFIG_FILE)
        self.CONNECTION = CommonDatabaseAPI.ET_CONNECTION
        self.RESOURCE = CommonDatabaseAPI.ET_RESOURCE

    def updateConnection(self, conn_id, conn_type=None, connecting_res_id=None, connected_res_id=None, **add_params):
        """ Update connection information.
        Find connection in database by ID and update all non-None passed attributes.
        """
        self.db_conn.connect()
        raw_connection = self.db_conn.get_entity(self.CONNECTION, conn_id)
        connection = Connection(raw_connection)

        #if description:
        #    connection.set_description(description)
        if connecting_res_id:
            connection.set_connecting_resource(connecting_res_id)
        if connected_res_id:
            connection.set_connected_resource(connected_res_id)

        for param_name, param_value in add_params.items():
            for key, value in param_value.iteritems():
                connection.set_attribute(key, value)

        self.db_conn.save_entity(self.CONNECTION, connection.to_dict())
        self.db_conn.close()

        return connection

    def getConnectionInfo(self, connection_id):
        """ Find connection in database by ID and return Connection object """
        self.db_conn.connect()
        raw_connection = self.db_conn.get_entity(self.CONNECTION, connection_id)
        self.db_conn.close()
        #connection = Connection(raw_connection)

        return Connection(raw_connection)

    def findConnection(self, connection_filter):
        """
        Find connection by filter and return found Connection objects.
        Filter should be dictionary where key = resource attribute with
        optional qualificator suffix (__in, __gt, __ge, __lw, __le, __all).
        """
        self.db_conn.connect()
        raw_connection = self.db_conn.find_entities(self.CONNECTION, connection_filter)
        self.db_conn.close()

        ret_list = []
        for conn in raw_connection:
            ret_list.append(Connection(conn))

        return ret_list

    def deleteConnection(self, coll_id):
        """ Delete connection by ID """
        self.db_conn.connect()
        self.db_conn.remove_entity(self.CONNECTION, coll_id)
        self.db_conn.close()

    def connectResources(self, conn_type, connecting_res_id, connected_res_id, conn_desc=None, **add_params):
        """ Connecting resource by connect type """
        filter_conn = {'specification_name': conn_type,
                       'connecting_resource': connecting_res_id,
                       'connected_resource': connected_res_id}

        if connecting_res_id == connected_res_id:
            raise BIException('Connection between similar resources is not allowed!')
        elif self.findConnection(filter_conn):
            raise BIException('Connection between resources already exist!')

        connection = Connection(specification_name=conn_type, connecting_resource=connecting_res_id,
                                connected_resource=connected_res_id, description=conn_desc,
                                additional_parameters=add_params)

        res = ResourceOperationalAPI()
        connecting_res = res.getResourceInfo(connecting_res_id)
        connected_res = res.getResourceInfo(connected_res_id)

        if connecting_res.to_dict() and connected_res.to_dict():
            spec = ManagementAPI()

            connecting_res_d = connecting_res.to_dict()
            connected_res_d = connected_res.to_dict()
            connecting_res_spec = spec.findSpecification(self.RESOURCE,
                                                         {'type_name': connecting_res_d['specification_name'],
                                                          'spec_type': self.RESOURCE})[0]
            connected_res_spec = spec.findSpecification(self.RESOURCE, {'type_name': connected_res_d['specification_name'],
                                                                          'spec_type': self.RESOURCE})[0]
            Resource.setup_specification([ResourceSpecification(connecting_res_spec.to_dict())])
            Resource.setup_specification([ResourceSpecification(connected_res_spec.to_dict())])

            connection.connect(connecting_res, connected_res)

            self.db_conn.connect()
            self.db_conn.save_entity(self.CONNECTION, connection.to_dict())
            self.db_conn.close()

    def disconnectResourcesById(self, connection_id):
        """Disconnect resource by connection ID """

        self.db_conn.connect()
        self.db_conn.remove_entity(self.CONNECTION, connection_id)
        self.db_conn.close()

    def disconnectResources(self, conn_type, connecting_res_id, connected_res_id):
        """Disconnect resource"""

        filter_conn = {'specification_name': conn_type,
                       'connecting_resource': connecting_res_id,
                       'connected_resource': connected_res_id}

        conn = self.findConnection(filter_conn)
        conn_id = ''
        for item in conn:
            conn_id = item.get__id()

        try:
            if conn_id:
                self.db_conn.connect()
                self.db_conn.remove_entity(self.CONNECTION, conn_id)
                self.db_conn.close()
        except Exception:
            raise BIException('Connection is not found! specification_name "%s",'
                              ' connecting_resource "%s", connected_resource "%s"' %
                              (conn_type, connecting_res_id, connected_res_id))

    def getLinkedResources(self, resource_id, conn_type=None, conn_direction=BOTH, **res_filter):
        """Get linked resource by direction"""

        if conn_direction in [BOTH, CONNECTING, CONNECTED]:
            if not isinstance(conn_direction, list):
                conn_direction = [conn_direction]
            result = []
            for direction in conn_direction:
                res_filter.update({'specification_name': conn_type, direction: resource_id})
                result.extend(self.findConnection(res_filter))
                del res_filter[direction]
            return result
        else:
            raise BIException('Connection directions "%s" is not correct!' % conn_direction)
