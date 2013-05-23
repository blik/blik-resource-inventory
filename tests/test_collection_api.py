from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
from blik.inventory.api.connection_oper_api import ConnectionOperationalAPI
from blik.inventory.api.collection_oper_api import CollectionOperationalAPI
from blik.inventory.core.base_entities import *
from blik.inventory.backend.common import *
from blik.inventory.backend.mongo import  MongoDatabaseAPI

import time
import unittest
from pymongo import objectid

DB_NAME = 'Test_BlikRI'
CONN_STRING = 'localhost:27017'

RESOURCE_LIST =[{"_id" : objectid.ObjectId("5010319237adc71128000001"), "specification_name" : "Switch", "res_status" : "standby", "owner" : "KST", "external_system" : "", "description" : "Portable computer of Konstantin Andrusenko", "additional_parameters" : {"Vendor" : "Apple", "model" : "MacBook Pro ", "memory" : 8192, "CPU" : "Intel Core i5"}},
                {"_id" : objectid.ObjectId("5010319237adc71128000002"), "specification_name" : "Switch", "res_status" : "standby", "owner" : "KST", "external_system" : "", "description" : "Portable computer of Konstantin Andrusenko", "additional_parameters" : {"Vendor" : "Apple", "model" : "MacBook Pro ", "memory" : 8192, "CPU" : "Intel Core i5"}},
                {"_id" : objectid.ObjectId("5010319237adc71128000004"), "specification_name" : "DSLAM", "res_status" : "down", "owner" : "Alex", "external_system" : "", "description" : "Portable computer of Aleksey Bogoslovskyi", "additional_parameters" : {"Vendor" : "Dell", "model" : "Vostro 1310", "memory" : 4096, "CPU" : "Intel Core2Duo T5670"}}]

SPEC_LIST = [{'type_name': 'l2vpn_site', 'allowed_types': ['Switch', 'Access'], 'params_spec': [{'param_name': 'test_param', 'param_type': 'integer'}]}]                

COLL_LIST = [{'_id': objectid.ObjectId('505b0df96998cb6fc9000010'), 'specification_name': 'l2vpn_site', 'resources': [], 'additional_parameters': {'test_param_2': {'id': 1}, 'test_param_1': 2}},
             {'_id': objectid.ObjectId('505b0df96998cb6fc9000011'), 'specification_name': 'l3vpn_site', 'resources': ['5010319237adc71128000001', '5010319237adc71128000002'], 'additional_parameters': {'test_param_2': {'id': 10}, 'test_param_1': 11}}]

def drop_test_database():
    from pymongo import Connection 
    conn = Connection()
    conn.drop_database(DB_NAME)
    conn.disconnect()

def insert_data(collection, obj_list):
    for item in obj_list:
        collection.insert(item)

def create_database_entities():
    from pymongo import Connection
    conn = Connection()
    insert_data(conn[DB_NAME][MongoDatabaseAPI.ET_COLLECTION], COLL_LIST)
    insert_data(conn[DB_NAME][MongoDatabaseAPI.ET_RESOURCE], RESOURCE_LIST)
    insert_data(conn[DB_NAME][MongoDatabaseAPI.ET_SPECIFICATION], SPEC_LIST)

    conn.disconnect()

class TestCollectionOperationalAPI(unittest.TestCase):
    def setUp(self):
        drop_test_database()
        create_database_entities()

    def check_exception(self,routine, exception=BIException):
        try:
            routine()
        except exception:
            pass
        except Exception, err:
            raise Exception('Exception <%s> is not expected in this case! Exception details: %s'% \
                            (err.__class__.__name__, err))
        else:
            raise Exception('Should be raised exception in this case')

    def get_collection(self):
        coll1 = {u'_id': '505b0df96998cb6fc9000010', u'specification_name': u'l2vpn_site', u'resources': [], 
                 u'additional_parameters': {u'test_param_2': {u'id': 1}, u'test_param_1': 200}}

        coll2 = {u'_id': '505b0df96998cb6fc9000010', u'specification_name': u'l2vpn_site', 
                 u'resources': ['5010319237adc71128000001', '5010319237adc71128000002'], u'additional_parameters': {u'test_param_2': {u'id': 1}, u'test_param_1': 2}}

        coll3 = {u'_id': '505b0df96998cb6fc9000011', u'specification_name': u'l3vpn_site',
                 u'resources': [u'5010319237adc71128000001'], u'additional_parameters': {u'test_param_2': {u'id': 10}, u'test_param_1': 11}}

        coll4 = {u'_id': '505b0df96998cb6fc9000011', u'specification_name': u'l3vpn_site', 
                 u'resources': [], u'additional_parameters': {u'test_param_2': {u'id': 10}, u'test_param_1': 11}}

        return coll1, coll2, coll3, coll4

    def create_spec(self):
        child_param_1 = {'param_name': 'idx',
                     'param_type': 'integer',
                     'description': 'interface parameter',
                     'mandatory': True}
        child_param_2 = {'param_name': 'id',
                     'param_type': 'integer',
                     'description': 'Board parameter',
                     'mandatory': False}

        param_1 = { 'param_name': 'interfaces',
                     'param_type': 'to_dict',
                     'description': 'Specify interface for Switch',
                     'mandatory': True,
                     #'possible_values': ['add_value'],
                     'default_value': 'default add value',
                     'children_spec': [child_param_1]}

        param_2 = { 'param_name': 'board',
                     'param_type': 'to_dict', #error with list type
                     'description': 'Specify board on Switch',
                     'mandatory': False,
                     'children_spec': [child_param_2]}
        spec = ResourceSpecification({'type_name': 'Switch', 'description': 'default spec for Switch'}, params_spec = [param_1, param_2])

        return spec

    def test_createCollection(self):
        time.sleep(1)
        collection = CollectionOperationalAPI()
        self.db_conn = MongoDatabaseAPI(CONN_STRING,DB_NAME)

        child_param = {'param_name': 'id',
                     'param_type': 'integer',
                     'description': 'interface parameter',
                     'mandatory': True}
        param_1 = { 'param_name': 'test_param_1',
                     'param_type': 'integer'}
        param_2 = { 'param_name': 'test_param_2',
                     'param_type': 'to_dict',
                     'children_spec': [child_param]}
        spec = CollectionSpecification({'type_name': 'l3vpn'}, allowed_types=['Switch', 'Access'], params_spec = [param_1, param_2])
        Collection.setup_specification([spec])
            #Parameter "test_param_2" is expected for "l3vpn" entity type!
        self.check_exception(lambda: collection.createCollection('l3vpn', test_param_1=1), BIValueError)

        coll_id = collection.createCollection('l3vpn', test_param_1=1, test_param_2={'id':1}).get__id()

        coll1 = {u'_id': str(coll_id), u'specification_name': u'l3vpn', u'resources': [], u'additional_parameters': {u'test_param_2': {u'id': 1}, u'test_param_1': 1}}
        self.db_conn.connect()
        find_coll = self.db_conn.find_entities('collection', {'specification_name': 'l3vpn'})
        self.db_conn.close()

        self.assertEqual(coll1, find_coll[0])

    def test_deleteCollection(self):
        time.sleep(1)
        collection = CollectionOperationalAPI()
        self.db_conn = MongoDatabaseAPI(CONN_STRING,DB_NAME)

        collection.deleteCollection('505b0df96998cb6fc9000010')

        self.db_conn.connect()
        self.check_exception(lambda: self.db_conn.get_entity('collection', '505b0df96998cb6fc9000010'), BIValueError)
        self.db_conn.close()

    def test_updateCollectionInfo(self):
        time.sleep(1)
        self.db_conn = MongoDatabaseAPI(CONN_STRING,DB_NAME)
        collection = CollectionOperationalAPI()

        collection.updateCollectionInfo('505b0df96998cb6fc9000010', additional_parameters={'test_param_1':200})

        self.db_conn.connect()
        find_coll = self.db_conn.get_entity('collection', '505b0df96998cb6fc9000010')
        self.db_conn.close()
        update_coll = self.get_collection()

        self.assertEqual(find_coll, update_coll[0])

    def test_appendResourceToCollection(self):
        time.sleep(1)
        res_spec = self.create_spec()
        Resource.setup_specification([res_spec])

        self.db_conn = MongoDatabaseAPI(CONN_STRING,DB_NAME)

        spec = CollectionSpecification({'type_name': 'l2vpn_site', 'allowed_types': ['Switch', 'Access']}, params_spec={'param_name': 'test_param', 'param_type': 'integer'})

        Collection.setup_specification([spec])
        collection = Collection()
        collection = CollectionOperationalAPI()
        collection.appendResourceToCollection('505b0df96998cb6fc9000010', '5010319237adc71128000001')
        collection.appendResourceToCollection('505b0df96998cb6fc9000010', '5010319237adc71128000002')
            #('Similar resources are not allowed in collection! resource "%s"', ObjectId('5010319237adc71128000002'))
        self.check_exception(lambda: collection.appendResourceToCollection('505b0df96998cb6fc9000010', '5010319237adc71128000002'), BIException)
            #Specification <DSLAM> is not registered!
        self.check_exception(lambda: collection.appendResourceToCollection('505b0df96998cb6fc9000010', '5010319237adc71128000004'), BIException)

        self.db_conn.connect()
        find_coll = self.db_conn.get_entity('collection', '505b0df96998cb6fc9000010')
        self.db_conn.close()

        coll = self.get_collection()
        self.assertEqual(coll[1], find_coll)

        spec = CollectionSpecification({'type_name': 'l2vpn_site', 'allowed_types': ['Access', 'DSLAM']}, params_spec={})
        Collection.setup_specification([spec])
        collection = Collection()
        collection = CollectionOperationalAPI()
            #Resource with type <Switch> is not allowed for collection <l2vpn_site>
        self.check_exception(lambda: collection.appendResourceToCollection('505b0df96998cb6fc9000010', '5010319237adc71128000001'), BIValueError)

    def test_removeResourceFromCollection(self):
        time.sleep(1)
        collection = CollectionOperationalAPI()
        self.db_conn = MongoDatabaseAPI(CONN_STRING,DB_NAME)

        collection.removeResourceFromCollection('505b0df96998cb6fc9000011','5010319237adc71128000002')

        self.db_conn.connect()
        find_coll = self.db_conn.get_entity('collection', '505b0df96998cb6fc9000011')
        coll = self.get_collection()

        self.assertEqual(coll[2], find_coll)

        collection.removeResourceFromCollection('505b0df96998cb6fc9000011','5010319237adc71128000001')
        find_coll = self.db_conn.get_entity('collection', '505b0df96998cb6fc9000011')
        coll = self.get_collection()
        self.db_conn.close()

        self.assertEqual(coll[3], find_coll)

            #Resource with ID "5010319237adc71128000001" is not exists in this collection.
        self.check_exception(lambda: collection.removeResourceFromCollection('505b0df96998cb6fc9000011','5010319237adc71128000001'), BIException)


if __name__ == '__main__':
    unittest.main()
                    