#!/usr/bin/env python
# -*- coding: utf-8 -*-
from blik.inventory.backend.common import *
from blik.inventory.backend.mongo import  MongoDatabaseAPI

from pymongo import objectid

SPEC_LIST = [{"_id" : objectid.ObjectId("5059769d6998cb10e2000222"), "spec_type" : "connection", 'type_name': 'L2',
'connecting_type': 'Switch', 'connected_type': 'Switch', 'params_spec':{'param_name': 'test_param_2','param_type': 'string'}},]

#{'params_spec': [{'param_name': 'Interface', 'param_type': 'dict', 'children_spec': [{'param_name': 'UPDATE_idx', 'param_type': 'integer','mandatory': True}]}, 
#                 {'param_name': 'Board', 'param_type': 'integer'}],
#'type_name': 'Switch', '_id': objectid.ObjectId('5059769d6998cb10e2000111'), 'spec_type': 'resource', 'parent_type_name': 'Parent Switch'}                


DB_NAME = 'Test_BlikRI'
CONN_STRING = 'localhost:27017'



def drop_test_database():
    from pymongo import Connection 
    conn = Connection()
    conn.drop_database(DB_NAME)
    conn.disconnect()

def insert_data(collection):
    num = ''
    item_list = []
    for i in range(10,100):
        num = '5059769d6998cb10e20002'+str(i)
        item1 = {"_id" : objectid.ObjectId(), "spec_type" : "connection", 'type_name': 'L2',
'connecting_type': 'Switch', 'connected_type': 'Switch', 'params_spec':{'param_name': 'test_param_2','param_type': 'string'}}
        item_list.append(item1)

    for i in range(10,100):
        item2 = {'params_spec': [{'param_name': 'Interface', 'param_type': 'dict', 'children_spec': [{'param_name': 'UPDATE_idx', 'param_type': 'integer','mandatory': True}]}, 
                                 {'param_name': 'Board', 'param_type': 'integer'}],
                'type_name': 'Switch', '_id': objectid.ObjectId(), 'spec_type': 'resource', 'parent_type_name': 'Parent Switch'}
        item_list.append(item2)

    for item in item_list:
        collection.insert(item)

def create_database_entities():
    from pymongo import Connection
    conn = Connection()
    insert_data(conn[DB_NAME][MongoDatabaseAPI.ET_SPECIFICATION])

    conn.disconnect()


if __name__ == '__main__':
    drop_test_database()
    create_database_entities()