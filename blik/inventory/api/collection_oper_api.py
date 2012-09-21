#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Purpose: Blik Inventory API for Collection
Created: 20.09.2012
Author: Yaroslav Chernyakov
"""

from blik.inventory.backend.mongo import  MongoDatabaseAPI
from blik.inventory.backend.common import  CommonDatabaseAPI
from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
from blik.inventory.core.inv_exceptions import BIException
from blik.inventory.core.base_entities import *

class CollectionOperationalAPI():
    def __init__ (self, conn_string, database):
        self.conn_string = conn_string
        self.database = database

        self.db_conn = MongoDatabaseAPI(self.conn_string, self.database)

    def createCollection(self, coll_type, **add_params):
        '''Create collection and save it into DB
        @return created collection object'''

        collection = Collection(specification_name=coll_type, additional_parameters=add_params)
        collection.validate()

        self.db_conn.connect()
        coll_id = self.db_conn.save_entity(CommonDatabaseAPI.ET_COLLECTION, collection.to_dict())
        self.db_conn.close()
        collection.set__id(coll_id)

        return collection

    def deleteCollection(self, coll_id):
        '''Delete collection by ID'''

        self.db_conn.connect()
        self.db_conn.remove_entity(CommonDatabaseAPI.ET_COLLECTION, coll_id)
        self.db_conn.close()

    def updateCollectionInfo(self, coll_id, **add_params):
        '''Update additional_parameters in collection'''

        self.db_conn.connect()
        raw_collection = self.db_conn.get_entity(CommonDatabaseAPI.ET_COLLECTION, coll_id)

        collection = Collection(raw_collection)

        for param_name, param_value in add_params.items():
            for key, value  in param_value.items():
                collection.set_attribute(key, value)

        self.db_conn.save_entity(CommonDatabaseAPI.ET_COLLECTION, collection.to_dict())
        self.db_conn.close()

        return collection

    def appendResourceToCollection(self, coll_id, res_id):
        '''Add resource to collection'''

        self.db_conn.connect()
        raw_collection = self.db_conn.get_entity(CommonDatabaseAPI.ET_COLLECTION, coll_id)
        collection = Collection(raw_collection)

        resource = ResourceOperationalAPI(self.conn_string, self.database)
        res = resource.getResourceInfo(res_id)

        collection.append_resource(res)
        self.db_conn.save_entity(CommonDatabaseAPI.ET_COLLECTION, collection.to_dict())
        self.db_conn.close()

    def removeResourceFromCollection(self, coll_id, res_id):
        '''Delete resource from collection'''

        self.db_conn.connect()
        raw_collection = self.db_conn.get_entity(CommonDatabaseAPI.ET_COLLECTION, coll_id)
        collection = Collection(raw_collection)

        resource = ResourceOperationalAPI(self.conn_string, self.database)
        res = resource.getResourceInfo(res_id)

        collection.remove_resource(res)
        self.db_conn.save_entity(CommonDatabaseAPI.ET_COLLECTION, collection.to_dict())
        self.db_conn.close()