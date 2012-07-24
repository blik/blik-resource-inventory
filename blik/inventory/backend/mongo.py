#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
from common import CommonDatabaseAPI
#from blik.inventory.core.inv_exceptions import *
from inv_exceptions import *


class MongoDatabaseAPI(CommonDatabaseAPI):
    def __init__(self, conn_string, database):
        if not database:
            raise BIException('Constructor of <%s> expect database parameter' %self.__class__.__name__)
        CommonDatabaseAPI.__init__(self, conn_string)
        self.database = database

    def connect(self):
        try:
            self.connection = pymongo.Connection(self.conn_string)
        except pymongo.errors.ConnectionFailure, err:
            raise BIException("Can't connect to DB. %s" %err)

    def close(self):
        self.connection.disconnect()

    def get_entity(self, ent_type, entity_id):
        collection = self.connection[self.database][ent_type]
        cursor = collection.find({"_id" : entity_id})
        #Try convert Mongo cursor to dictionary
        try:
            return cursor[0]
        except:
            return None

    def find_entities(self, ent_type, obj_filter):
        collection = self.connection[self.database][ent_type]
        if not obj_filter:
            cursor = collection.find()
        else:
            if not isinstance(obj_filter, dict):
                raise BIValueError("Function find_entities of <%s> expect dictionary as obj_filter parameter!" %self.__class__.__name__)
            query = {}
            for key, value in obj_filter.items():
                k = key.split("__")
                if k[-1] in ["gt", "gte", "lt", "lte", "ne", "in", "nin", "all"]:
                    query["__".join(k[0:-1])] = {"$"+str(k[-1]) : value}
                else:
                    query[key] = value
        cursor = collection.find(query)
        entities = []
        for item in cursor:
            entities.append(item)
        return entities

    def save_entity(self, ent_type, entity_dict):
        if not isinstance(entity_dict, dict):
            raise BIValueError("Function save_entity of <%s> expect dictionary as entity_dict parameter!" %self.__class__.__name__)
        collection = self.connection[self.database][ent_type]
        if "_id" in entity_dict:
            collection.update({"_id": entity_dict["_id"]}, entity_dict, upsert=True)
        else:
            raise BIValueError("Function save_entity of <%s> must have '_id' key in input dictionary" %self.__class__.__name__)

    def remove_entity(self, ent_type, entity_id):
        collection = self.connection[self.database][ent_type]
        collection.remove({"_id": entity_id})
