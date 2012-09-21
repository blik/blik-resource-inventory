#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Purpose: Blik Inventory API for Connection
Created: 20.09.2012
Author: Yaroslav Chernyakov
"""

from blik.inventory.backend.common import  CommonDatabaseAPI
from blik.inventory.backend.mongo import  MongoDatabaseAPI
from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
from blik.inventory.core.inv_exceptions import BIException
from blik.inventory.core.base_entities import *

BOTH = ['connecting_resource', 'connected_resource']
CONNECTING = 'connecting_resource'
CONNECTED = 'connected_resource'

class ConnectionOperationalAPI():
    def __init__(self, conn_string, database):
        self.conn_string = conn_string
        self.database = database

        self.db_conn = MongoDatabaseAPI(self.conn_string, self.database)

    def updateConnection(self, conn_id, conn_type=None, connecting_res_id=None, connected_res_id=None, **add_params ):
        '''Update connection information.
        Find connection in database by ID and update all non-None passed attributes.
        '''

        self.db_conn.connect()
        res = ResourceOperationalAPI(self.conn_string, self.database)
        raw_connection = self.db_conn.get_entity(CommonDatabaseAPI.ET_CONNECTION, conn_id)

        connection = Connection(raw_connection)

        if conn_type != None:
            connection.set_specification_name(conn_type)
        if connecting_res_id != None:
            connection.set_connecting_resource(connecting_res_id)
            self.connecting_res = res.getResourceInfo(connecting_res_id)
        if connected_res_id != None:
            connection.set_connected_resource(connected_res_id)
            self.connected_res = res.getResourceInfo(connected_res_id)

        for param_name, param_value in add_params.items():
            for key, value  in param_value.items():
                connection.set_attribute(key, value)

        connection.connect(self.connecting_res, self.connected_res)

        self.db_conn.save_entity(CommonDatabaseAPI.ET_CONNECTION, connection.to_dict())
        self.db_conn.close()

        return connection

    def findConnection(self, connection_filter):
        '''Find connection by filter and return found Connection objects.
        Filter should be dictionary where key = resource attribute with
        optional qualificator suffix (__in, __gt, __ge, __lw, __le, __all).
        '''

        self.db_conn.connect()
        raw_connection = self.db_conn.find_entities(CommonDatabaseAPI.ET_CONNECTION, connection_filter)
        self.db_conn.close()

        ret_list = []
        for conn in raw_connection:
            ret_list.append(Connection(conn))

        return ret_list

    def connectResources(self, conn_type, connecting_res_id, connected_res_id, **add_params):
        '''Connecting resource by connect type'''
        filter_conn = {'specification_name': conn_type,
                       'connecting_resource': connecting_res_id,
                       'connected_resource': connected_res_id}

        if connecting_res_id == connected_res_id:
            raise BIException('Connection between similar resources is not allowed!')
        elif self.findConnection(filter_conn):
            raise BIException('Connection between resources "%s" and "%s" by type "%s" already exist!'%(connecting_res_id, connected_res_id, conn_type))

        connection = Connection(specification_name=conn_type, connecting_resource=connecting_res_id,  connected_resource=connected_res_id, additional_parameters=add_params)

        res = ResourceOperationalAPI(self.conn_string, self.database)
        connecting_res = res.getResourceInfo(connecting_res_id)
        connected_res = res.getResourceInfo(connected_res_id)

        if connecting_res.to_dict() and connected_res.to_dict():
            connection.connect(connecting_res, connected_res)
            self.db_conn.connect()
            self.db_conn.save_entity(CommonDatabaseAPI.ET_CONNECTION, connection.to_dict())
            self.db_conn.close()

    def disconnectResourcesById(self, connection_id):
        '''Disconnect resource by connection ID '''

        self.db_conn.connect()
        self.db_conn.remove_entity(CommonDatabaseAPI.ET_CONNECTION, connection_id)
        self.db_conn.close()

    def disconnectResources(self, conn_type, connecting_res_id, connected_res_id):
        '''Disconnect resource'''

        filter_conn = {'specification_name': conn_type,
                       'connecting_resource': connecting_res_id,
                       'connected_resource': connected_res_id}

        conn = self.findConnection(filter_conn)
        for item in conn:
            conn_id = item.get__id()
        try:
            if conn_id:
                self.db_conn.connect()
                self.db_conn.remove_entity(CommonDatabaseAPI.ET_CONNECTION, conn_id)
                self.db_conn.close()
        except Exception:
            raise BIException('Connection is not found! specification_name "%s", connecting_resource "%s", connected_resource "%s"'%
                              (conn_type, connecting_res_id, connected_res_id))

    def getLinkedResources(self, resource_id, conn_type=None, conn_direction=BOTH):
        '''Get linked resource by direction'''

        filter_conn = {'specification_name': conn_type, CONNECTING: resource_id}
        filter_conned = {'specification_name': conn_type, CONNECTED: resource_id}

        if conn_direction == BOTH:
            list_1 = []
            connecting_list = self.findConnection(filter_conn)
            connected_list = self.findConnection(filter_conned)
            for item in connecting_list:
                list_1.append(item)
            for item in connected_list:
                list_1.append(item)
            return list_1
        elif conn_direction == CONNECTING:
            return self.findConnection(filter_conn)
        elif conn_direction == CONNECTED:
            return self.findConnection(filter_conned)
        else:
            raise BIException ('Connection directions "%s" is not correct!'%conn_direction)    