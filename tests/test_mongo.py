#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from pymongo import Connection, objectid
from blik.inventory.backend.mongo import MongoDatabaseAPI
from blik.inventory.core.inv_exceptions import *
import time

DB_NAME = "Test_BlikRI"

RESOURCE_LIST = [{"_id" : objectid.ObjectId("5010319237adc71128000000"), "res_type" : "computer", "res_status" : "active", "owner" : "YAC", "external_system" : "", "description" : "Portable computer of Yaroslav Chernyakov", "additional_parameters" : {"Vendor" : "Dell", "model" : "XPS 15z", "memory" : 6144, "CPU" : "Intel Core i5"}},
                {"_id" : objectid.ObjectId("5010319237adc71128000001"), "res_type" : "computer", "res_status" : "standby", "owner" : "KST", "external_system" : "", "description" : "Portable computer of Konstantin Andrusenko", "additional_parameters" : {"Vendor" : "Apple", "model" : "MacBook Pro ", "memory" : 8192, "CPU" : "Intel Core i5"}},
                {"_id" : objectid.ObjectId("5010319237adc71128000002"), "res_type" : "computer", "res_status" : "down", "owner" : "Alex", "external_system" : "", "description" : "Portable computer of Aleksey Bogoslovskyi", "additional_parameters" : {"Vendor" : "Dell", "model" : "Vostro 1310", "memory" : 4096, "CPU" : "Intel Core2Duo T5670"}},
                {"_id" : objectid.ObjectId("5010319237adc71128000003"), "res_type" : "switch", "res_status" : "active", "owner" : "Priocom", "external_system" : "", "description" : "Some Priocom's Device", "additional_parameters" : {"Vendor" : "Cisco", "model" : "Catalist 3100", "port_speed" : ["10Mb/s"]}},
                {"_id" : objectid.ObjectId("5010319237adc71128000004"), "res_type" : "switch", "res_status" : "standby", "owner" : "Ukrtelecom", "external_system" : "", "description" : "Some Ukrtelecom's Device", "additional_parameters" : {"Vendor" : "Cisco", "model" : "Catalist 6503", "port_speed" : ["10Mb/s", "100Mb/s", "1Gb/s", "10Gb/s"]}},
                {"_id" : objectid.ObjectId("5010319237adc71128000005"), "res_type" : "printer", "res_status" : "down", "owner" : "Alex", "external_system" : "", "description" : "Printer of Aleksey Bogoslovskyi", "additional_parameters" : {"Vendor" : "HP", "model" : "1020"}},
                {"_id" : objectid.ObjectId("5010319237adc71128000006"), "res_type" : "router", "res_status" : "down", "owner" : "Priocom", "external_system" : "", "description" : "Cisco router 2900 series", "additional_parameters" : {"Vendor" : "Cisco", "model" : "2911", "memory" : 1024, "port_speed" : ["10Mb/s", "100Mb/s"]}},
                {"_id" : objectid.ObjectId("5010319237adc71128000007"), "res_type" : "router", "res_status" : "active", "owner" : "KST", "external_system" : "", "description" : "Home router of Konstantin Andrusenko", "additional_parameters" : {"Vendor" : "TP-Link", "model" : "TL-WR841", "memory" : 32, "port_speed" : ["10Mb/s", "100Mb/s"]}},
                {"_id" : objectid.ObjectId("5010319237adc71128000008"), "res_type" : "router", "res_status" : "active", "owner" : "Alex", "external_system" : "", "description" : "Home router of Aleksey Bogoslovskyi", "additional_parameters" : {"Vendor" : "Zyxel", "model" : "Keenetic", "memory" : 32, "port_speed" : ["10Mb/s", "100Mb/s", "480Mb/s" ]}},
                {"_id" : objectid.ObjectId("5010319237adc71128000009"), "res_type" : "modem", "res_status" : "down", "owner" : "KST", "external_system" : "", "description" : "Mobile modem of Konstantin Andrusenko", "additional_parameters" : {"Mobile Operator" : "MTS", "Vendor" : "ZTE"}}]


def drop_test_database():
    conn = Connection()
    conn.drop_database(DB_NAME)
    conn.disconnect()

def insert_data(collection, obj_list):
    for item in obj_list:
        collection.insert(item)

def create_database_entities():
    conn = Connection()
    insert_data(conn[DB_NAME][MongoDatabaseAPI.ET_RESOURCE], RESOURCE_LIST)
    conn.disconnect()

class TestMongoAPI(unittest.TestCase):
    def test_01_connect(self):
        #   Try connect to DB when given wrong port type
        connection = MongoDatabaseAPI("localhost:wrong_port", DB_NAME)
        self.assertRaises(BIValueError, connection.connect)

        #   Try connect to DB when given wrong connection string
        connection = MongoDatabaseAPI("localhost:100500", DB_NAME)
        self.assertRaises(BIException, connection.connect)

    def test_02_get_entity(self, entity_id = "5010319237adc71128000001"):
        connection = MongoDatabaseAPI("localhost", DB_NAME)
        connection.connect()

        #   Try get information about entity that not exist
        self.assertRaises(BIValueError, connection.get_entity, MongoDatabaseAPI.ET_RESOURCE, "some_fake_id")

        #   Get information about entity that exist
        api_result = connection.get_entity(MongoDatabaseAPI.ET_RESOURCE, entity_id)
        result = {"_id" : objectid.ObjectId("5010319237adc71128000001"), "res_type" : "computer", "res_status" : "standby", "owner" : "KST", "external_system" : "", "description" : "Portable computer of Konstantin Andrusenko", "additional_parameters" : {"Vendor" : "Apple", "model" : "MacBook Pro ", "memory" : 8192, "CPU" : "Intel Core i5"}}
        self.assertEqual(api_result, result)

        connection.close()

    def test_03_find_entities(self):
        connection = MongoDatabaseAPI("localhost", DB_NAME)
        connection.connect()
        #   Given wrong object filter type
        self.assertRaises(BIValueError, connection.find_entities, MongoDatabaseAPI.ET_RESOURCE, "fake_object_filter_type")
        conn = Connection()
        result = []
        for item in conn[DB_NAME][MongoDatabaseAPI.ET_RESOURCE].find({}):
            result.append(item)

        #   Find all entities
        api_result = connection.find_entities("resource")
        self.assertEqual(api_result.sort(), RESOURCE_LIST.sort())

        #   Find entities with "ne" and "in"
        api_result = connection.find_entities("resource", {"res_status__ne": "active", "res_type__in": ["switch", "printer"]})
        result = [{u'res_type': u'switch', u'description': u"Some Ukrtelecom's Device", u'additional_parameters': {u'model': u'Catalist 6503', u'Vendor': u'Cisco', u'port_speed': [u'10Mb/s', u'100Mb/s', u'1Gb/s', u'10Gb/s']}, u'owner': u'Ukrtelecom', u'_id': objectid.ObjectId('5010319237adc71128000004'), u'external_system': u'', u'res_status': u'standby'}, 
                  {u'res_type': u'printer', u'description': u'Printer of Aleksey Bogoslovskyi', u'additional_parameters': {u'model': u'1020', u'Vendor': u'HP'}, u'owner': u'Alex', u'_id': objectid.ObjectId('5010319237adc71128000005'), u'external_system': u'', u'res_status': u'down'}]
        self.assertEqual(api_result.sort(), result.sort())

        #   Find entities with "equal" and "nin"
        api_result = connection.find_entities("resource", {"res_status": "active", "res_type__nin": ["router", "modem", "switch"]})
        result = [{u'res_type': u'computer', u'description': u'Portable computer of Yaroslav Chernyakov', u'additional_parameters': {u'model': u'XPS 15z', u'Vendor': u'Dell', u'CPU': u'Intel Core i5', u'memory': 6144}, u'owner': u'YAC', u'_id': objectid.ObjectId('5010319237adc71128000000'), u'external_system': u'', u'res_status': u'active'}]
        self.assertEqual(api_result.sort(), result.sort())

        #   Use nested dict
        api_result = connection.find_entities("resource", {"additional_parameters.memory__gte": 1024, "_id__nin":["5010319237adc71128000006", "5010319237adc71128000000", "5010319237adc71128000001"]})
        result = [{u'res_type': u'computer', u'description': u'Portable computer of Aleksey Bogoslovskyi', u'additional_parameters': {u'model': u'Vostro 1310', u'Vendor': u'Dell', u'CPU': u'Intel Core2Duo T5670', u'memory': 4096}, u'owner': u'Alex', u'_id': objectid.ObjectId('5010319237adc71128000002'), u'external_system': u'', u'res_status': u'down'}]
        self.assertEqual(api_result.sort(), result.sort())
        connection.close()

    def test_04_save_entity(self):
        connection = MongoDatabaseAPI("localhost", DB_NAME)
        connection.connect()
        #   Given wrong record type to save
        self.assertRaises(BIValueError, connection.save_entity, MongoDatabaseAPI.ET_RESOURCE, "not a dict value")

        #   Insert new record("_id" exist in incoming dictionary but not in DB)
        new_record = {"_id" : objectid.ObjectId("5010cb8137adc7191b000000"), "res_type" : "printer", "res_status" : "active", "owner" : "Priocom", "external_system" : "", "description" : "Printer in the Brannigan Team workroom", "additional_parameters" : {"Vendor" : "Canon", "model" : "iR1018"}}
        
        id = connection.save_entity(MongoDatabaseAPI.ET_RESOURCE, new_record)
        conn = Connection()
        result = conn[DB_NAME][MongoDatabaseAPI.ET_RESOURCE].find_one({'_id': objectid.ObjectId(id)})
        self.assertEqual(new_record, result)

        #   Insert another new record(no "_id" key in incoming dictionary)
        new_record = {"res_type" : "printer", "res_status" : "active", "owner" : "Priocom", "external_system" : "", "description" : "Printer in the Brannigan Team workroom", "additional_parameters" : {"Vendor" : "Canon", "model" : "iR1018"}}
        id = connection.save_entity(MongoDatabaseAPI.ET_RESOURCE, new_record)
        conn = Connection()
        result = conn[DB_NAME][MongoDatabaseAPI.ET_RESOURCE].find_one({'_id': objectid.ObjectId(id)})
        self.assertEqual(new_record, result)

        #   Update existing record(change res_status and additional_parameters:model)
        new_record = {"_id": id, "res_type" : "printer", "res_status" : "down", "owner" : "Priocom", "external_system" : "", "description" : "Printer in the Brannigan Team workroom", "additional_parameters" : {"Vendor" : "Canon", "model" : "iR1022"}}
        id = connection.save_entity(MongoDatabaseAPI.ET_RESOURCE, new_record)
        result = conn[DB_NAME][MongoDatabaseAPI.ET_RESOURCE].find_one({'_id': objectid.ObjectId(id)})
        self.assertEqual(new_record, result)

        conn.disconnect()
        connection.close()

    def test_05_remove_entity(self):
        connection = MongoDatabaseAPI("localhost", DB_NAME)
        connection.connect()
        conn = Connection()

        #   Check that record is exist in DB
        result = conn[DB_NAME][MongoDatabaseAPI.ET_RESOURCE].find_one({'_id': objectid.ObjectId('5010cb8137adc7191b000000')})
        self.assertNotEqual(result, None)

        #   Remove record and check again
        connection.remove_entity(MongoDatabaseAPI.ET_RESOURCE, "5010cb8137adc7191b000000")
        result = conn[DB_NAME][MongoDatabaseAPI.ET_RESOURCE].find_one({'_id': objectid.ObjectId('5010cb8137adc7191b000000')})
        self.assertEqual(result, None)

        #   Remove record that was deleted at previous step
        connection.remove_entity(MongoDatabaseAPI.ET_RESOURCE, "5010cb8137adc7191b000000")
        result = conn[DB_NAME][MongoDatabaseAPI.ET_RESOURCE].find_one({'_id': objectid.ObjectId('5010cb8137adc7191b000000')})
        self.assertEqual(result, None)

        conn.disconnect()
        connection.close()

if __name__ == '__main__':
    drop_test_database()
    create_database_entities()
    time.sleep(1)
    unittest.main()