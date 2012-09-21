import unittest
import time
from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
from blik.inventory.api.connection_oper_api import ConnectionOperationalAPI
from blik.inventory.core.base_entities import *
from blik.inventory.backend.common import *

from pymongo import Connection, objectid
from blik.inventory.backend.mongo import MongoDatabaseAPI

DB_NAME = 'TEST_RES_API'
ET_RESOURCE = 'resource'

RESOURCE_LIST =[{"_id" : objectid.ObjectId("5010319237adc71128000000"), "specification_name" : "Switch", "resource_status" : "standby", "owner" : "KST", "external_system" : "", "description" : "Portable computer", 
                   "additional_parameters": {'interfaces': {'idx': 2,'name': 'eth0','mac': '10:10:10:10:10'}, 'board': {'id': [1,2]}}},
                {"_id" : objectid.ObjectId("5010319237adc71128000001"), "specification_name" : "Switch", "resource_status" : "active", "owner" : "YAC", "external_system" : "", "description" : "Portable computer", 
                   "additional_parameters": {'interfaces': {'idx': 1,'name': 'eth2','mac': '10:10:10:10:11'}, 'board': {'id': 5}}}]

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

class TestResourceOperationalAPI(unittest.TestCase):
    def setUp(self):
        #time.sleep(1)
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
    def get_resources(self):
        res1 = {u'description': u'update description', u'additional_parameters': {u'interfaces': {u'mac': u'10:10:10:10:10', u'name': u'eth0', u'idx': 2}, u'board': {u'id': [1, 2]}}, 
                u'specification_name': u'Switch', u'resource_status': u'Blocked_new', u'owner': u'update owner', u'location': u'update location', 
                u'department': u'update department', u'_id': '5010319237adc71128000000', u'external_system': u'update external_system'} 

        res2 = {u'description': u'update2 description', u'additional_parameters': {u'interfaces': {u'new_param': u'new_value222', u'mac': u'10:10:10:10:12', u'name': u'updated eth0', u'idx': 2}, u'board': 3},
                u'specification_name': u'Switch', u'resource_status': u'Active_new', u'department': u'update department', u'location': u'update location', u'owner': u'update owner',
                u'_id': '5010319237adc71128000000', u'external_system': u'update external_system'}

        res3 = {u'description': u'Portable computer', u'additional_parameters': {u'interfaces': {u'mac': u'10:10:10:10:10', u'name': u'eth0', u'idx': 2}, u'board': {u'id': [1, 2]}},
                u'specification_name': u'Switch', u'resource_status': u'standby', u'owner': u'KST', u'_id': '5010319237adc71128000000', u'external_system': u''}

        return res1, res2, res3

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

    def test_create_resources(self):
        self.maxDiff = None
        time.sleep(1)
        specs = self.create_spec()
        Resource.setup_specification([specs])

        resource = ResourceOperationalAPI('localhost', DB_NAME)
        self.db_conn = MongoDatabaseAPI('localhost',DB_NAME)
        
        self.check_exception(lambda: resource.createResource('Switch'), TypeError)
        self.check_exception(lambda: resource.createResource('DSLAM', 'New', interfaces={}), BIValueError) #incorrect DSLAM type
        self.check_exception(lambda: resource.createResource('Switch', 'New'), BIValueError) #interfaces is need

        res1_id = resource.createResource('Switch', 'Blocked', 'Test Switch device', interfaces={}).get__id()
        res1 = {u'description': u'Test Switch device', u'additional_parameters': {u'interfaces': {}}, u'specification_name': u'Switch', 
                u'resource_status': u'Blocked', u'department': None, u'location': None, u'owner': None, u'_id': str(res1_id), u'external_system': None}

        self.db_conn.connect()
        find_res = self.db_conn.find_entities('resource', {"resource_status" : "Blocked"})

        self.assertEqual(res1, find_res[0])

        res2_id = resource.createResource('Switch', 'Active', 'description Switch device', 'test external system', 'test location', 'test department', 'test owner',
                                                interfaces={'idx': 1,
                                                             'name': 'eth0',
                                                             'mac': '10:10:10:10:10'},
                                                board={'id': [1,2,3,4,5]}).get__id()
        res2 = {u'description': u'description Switch device', u'additional_parameters': {u'interfaces': {u'mac': u'10:10:10:10:10', u'name': u'eth0', u'idx': 1}, u'board': {u'id': [1, 2, 3, 4, 5]}},
               u'specification_name': u'Switch', u'resource_status': u'Active', u'department': u'test department', u'location': u'test location', u'owner': u'test owner', 
               u'_id': str(res2_id), u'external_system': u'test external system'}
        find_res = self.db_conn.find_entities('resource', {"resource_status" : "Active"})
        self.db_conn.close()

        self.assertEqual(res2, find_res[0])

    def test_updateResource(self):
        self.maxDiff = None
        time.sleep(1)
        specs = self.create_spec()
        Resource.setup_specification([specs])

        resource = ResourceOperationalAPI('localhost', DB_NAME)
        self.db_conn = MongoDatabaseAPI('localhost',DB_NAME)
        self.db_conn.connect()
        
        self.check_exception(lambda: resource.updateResource(), TypeError)
            #Parameter "new param" is not expected for "Switch" entity type
        self.check_exception(lambda: resource.updateResource('5010319237adc71128000000', 'Active', 'update description',additional_parameters={'new param': 'new value'}), BIValueError)
            #without update additional_parameters
        resource.updateResource('5010319237adc71128000000', 'Blocked_new', 'update description', 'update external_system', 'update location', 'update department', 'update owner',
                                                additional_parameters={})

        res1 = self.get_resources()
        updated_res = self.db_conn.get_entity('resource', '5010319237adc71128000000')

        self.assertEqual(res1[0], updated_res)

            #update with additional_parameters
        resource.updateResource('5010319237adc71128000000', 'Active_new', 'update2 description',
                                                additional_parameters={'interfaces': {'idx': 2,'name': 'updated eth0','mac': '10:10:10:10:12','new_param': 'new_value222'},
                                                                       'board': 3})
        res2 = self.get_resources()
        updated_res = self.db_conn.get_entity('resource', '5010319237adc71128000000')
        self.db_conn.close()

        self.assertEqual(res2[1], updated_res)

    def test_getResourceInfo(self):
        self.maxDiff = None
        time.sleep(1)
        resource = ResourceOperationalAPI('localhost', DB_NAME)
        self.db_conn = MongoDatabaseAPI('localhost',DB_NAME)
        
        resource.getResourceInfo('5010319237adc71128000000')

        res = self.get_resources()
        self.db_conn.connect()
        resources = self.db_conn.get_entity('resource', '5010319237adc71128000000')
        self.db_conn.close()

        self.assertEqual(res[2], resources) 

    def test_findResources(self):
        time.sleep(1)
        resource = ResourceOperationalAPI('localhost', DB_NAME)
        self.db_conn = MongoDatabaseAPI('localhost',DB_NAME)
        self.db_conn.connect()
        
        resources = self.db_conn.find_entities('resource', {'resource_status__in': ['standby', 'active']})
        self.db_conn.close()

        self.assertEqual(2, len(resources))

    def test_removeResource(self):
        time.sleep(1)
        resource = ResourceOperationalAPI('localhost', DB_NAME)
        self.db_conn = MongoDatabaseAPI('localhost',DB_NAME)
        
        resource.removeResource('5010319237adc71128000000')
        self.db_conn.connect()
            #Can't find information about record with entity_id 5010319237adc71128000000 in resource collection
        self.check_exception(lambda: self.db_conn.get_entity('resource','5010319237adc71128000000'), BIValueError)
        self.db_conn.close()

if __name__ == '__main__':
    unittest.main()