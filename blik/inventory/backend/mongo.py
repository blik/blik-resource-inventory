#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Purpose: Blik Inventory API to Mongo DB
Created: 26.08.2012
Author:  Aleksey Bogoslovskyi
"""

from pymongo import Connection, errors, objectid
from common import CommonDatabaseAPI
from blik.inventory.core.inv_exceptions import *


class MongoDatabaseAPI(CommonDatabaseAPI):
    def __init__(self, conn_string, database):
        if not database:
            raise BIException('Constructor of <%s> expect database parameter' % self.__class__.__name__)
        CommonDatabaseAPI.__init__(self, conn_string)
        self.database = database

    def connect(self):
        """
        Open connection to DB
        """
        try:
            self.connection = Connection(self.conn_string)
        except errors.ConfigurationError, err:
            raise BIValueError("Error in connection string parameter.\n%s" % err)
        except errors.ConnectionFailure, err:
            raise BIException("Can't connect to DB.\n%s" % err)

    def close(self):
        """
        Close connection to DB
        """
        self.connection.disconnect()

    def _check_ent_type(self, ent_type):
        if ent_type not in self.SUPPORTED_ENT_TYPES:
            raise BIValueError("Entity type \"%s\" is not supported" % ent_type)

    def get_entity(self, ent_type, entity_id):
        """
        Get information about entity by incoming identifier
        """
        self._check_ent_type(ent_type)
        collection = self.connection[self.database][ent_type]
        cursor = collection.find_one({"_id": objectid.ObjectId(str(entity_id))})

        if cursor:
            cursor["_id"] = str(cursor["_id"])
            return cursor
        else:
            raise BIValueError("Can't find information about record with entity_id %s in %s collection" %
                               (entity_id, ent_type))

    def _get_filter_query(self, obj_filter):
        query = {}
        if obj_filter:
            if not isinstance(obj_filter, dict):
                raise BIValueError("Function find_entities of <%s> expect dictionary as obj_filter parameter!" %
                                   self.__class__.__name__)
            for key, value in obj_filter.items():
                k = key.split("__")
                if key.startswith("_id"):
                    if isinstance(value, list):
                        new = []
                        for item in value:
                            new.append(str(objectid.ObjectId(str(item))))
                        value = new
                    else:
                        value = objectid.ObjectId(str(value))
                if k[-1] in ["gt", "gte", "lt", "lte", "ne", "in", "nin", "all"]:
                    query["__".join(k[0:-1])] = {"$" + str(k[-1]): value}
                else:
                    query[key] = value

        return query

    def find_entities(self, ent_type, obj_filter=None):
        """
        Find DB records by incoming filter
        """
        self._check_ent_type(ent_type)
        collection = self.connection[self.database][ent_type]
        entities = []
        for item in collection.find(self._get_filter_query(obj_filter)):
            item["_id"] = str(item["_id"])
            entities.append(item)

        return entities

    def save_entity(self, ent_type, entity_dict):
        """
        Create new or update existing record in DB
        """
        self._check_ent_type(ent_type)
        if not isinstance(entity_dict, dict):
            raise BIValueError("Function save_entity of <%s> expect dictionary as entity_dict parameter!" %
                               self.__class__.__name__)
        collection = self.connection[self.database][ent_type]
        if "_id" in entity_dict:
            entity_dict["_id"] = objectid.ObjectId(str(entity_dict["_id"]))
            collection.update({"_id": entity_dict["_id"]}, entity_dict, upsert=True)
        else:
            entity_dict["_id"] = collection.insert(entity_dict)
        return entity_dict["_id"]

    def remove_entity(self, ent_type, entity_id):
        """
        Delete record from DB
        """
        self._check_ent_type(ent_type)
        collection = self.connection[self.database][ent_type]
        collection.remove({"_id" : objectid.ObjectId(str(entity_id))})