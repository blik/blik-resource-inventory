#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Purpose: Blik Inventory API for Collection
Created: 20.09.2012
Author: Yaroslav Chernyakov
"""

from blik.inventory.utils.ri_spec_manager import  InventoryConfiguration
from blik.inventory.backend.common import  CommonDatabaseAPI
from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
from blik.inventory.core.inv_exceptions import BIException
from blik.inventory.core.base_entities import *

CONFIG_FILE = "/opt/blik/inventory/conf/blik-ri-conf.yaml"

class CollectionOperationalAPI():
    def __init__ (self):
        self.conf = InventoryConfiguration()
        self.db_conn = self.conf.get_backend_db(CONFIG_FILE)

    def createCollection(self, coll_type, description, **add_params):
        '''Create collection and save it into DB
        @return created collection object'''

        collection = Collection(specification_name=coll_type, description=description, additional_parameters=add_params.itervalues().next())
        collection.validate()

        self.db_conn.connect()
        coll_id = self.db_conn.save_entity(CommonDatabaseAPI.ET_COLLECTION, collection.to_dict())
        self.db_conn.close()
        collection.set__id(coll_id)

        return collection

    def getCollectionInfo(self, collection_id):
        '''Find collection in database by ID and return Collection object
        '''

        self.db_conn.connect()
        raw_collection = self.db_conn.get_entity(CommonDatabaseAPI.ET_COLLECTION, collection_id)
        self.db_conn.close()

        collection = Collection(raw_collection)

        return collection

    def findCollections(self, coll_filter):
        '''Find collection by filter and return found Collection objects
        Filter should be dictionary where key = resource attribute with
        optional qualificator suffix (__in, __gt, __ge, __lw, __le)
        '''

        self.db_conn.connect()
        raw_collection = self.db_conn.find_entities(CommonDatabaseAPI.ET_COLLECTION, coll_filter)
        self.db_conn.close()

        ret_list = []
        for res in raw_collection:
            ret_list.append(Collection(res))

        return ret_list

    def deleteCollection(self, coll_id):
        '''Delete collection by ID'''

        self.db_conn.connect()
        self.db_conn.remove_entity(CommonDatabaseAPI.ET_COLLECTION, coll_id)
        self.db_conn.close()

    def updateCollectionInfo(self, coll_id, description=None, **add_params):
        '''Update additional_parameters in collection'''

        self.db_conn.connect()
        raw_collection = self.db_conn.get_entity(CommonDatabaseAPI.ET_COLLECTION, coll_id)

        collection = Collection(raw_collection)
        if description:
            collection.set_description(description)

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

        resource = ResourceOperationalAPI()
        res = resource.getResourceInfo(res_id)

        collection.append_resource(res)
        self.db_conn.save_entity(CommonDatabaseAPI.ET_COLLECTION, collection.to_dict())
        self.db_conn.close()

    def removeResourceFromCollection(self, coll_id, res_id):
        '''Delete resource from collection'''

        self.db_conn.connect()
        raw_collection = self.db_conn.get_entity(CommonDatabaseAPI.ET_COLLECTION, coll_id)
        collection = Collection(raw_collection)

        resource = ResourceOperationalAPI()
        res = resource.getResourceInfo(res_id)

        collection.remove_resource(res)
        self.db_conn.save_entity(CommonDatabaseAPI.ET_COLLECTION, collection.to_dict())
        self.db_conn.close()