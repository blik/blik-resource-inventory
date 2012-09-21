from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
from blik.inventory.api.connection_oper_api import ConnectionOperationalAPI
from blik.inventory.core.base_entities import *
from blik.inventory.backend.common import *
from blik.inventory.backend.mongo import  MongoDatabaseAPI

import time
import unittest
from pymongo import objectid

DB_NAME = 'TEST_CONN_API'

CONN_LIST = [{"_id" : objectid.ObjectId("5010319237adc71128000000"), "connecting_resource" : "5010319237adc71128000001", "specification_name" : "L2", "connected_resource" : "5010319237adc71128000002", "additional_parameters" : { "Port_one" : 10, "Port_two" : 30}},
             {"_id" : objectid.ObjectId("5010319237adc71128000005"), "connecting_resource" : "5010319237adc71128000010", "specification_name" : "Test", "connected_resource" : "5010319237adc71128000009", "additional_parameters" : { "Port_one" : 1, "Port_two" : 3}},
             {"_id" : objectid.ObjectId("5010319237adc71128000006"), "connecting_resource" : "5010319237adc71128000011", "specification_name" : "NEW", "connected_resource" : "5010319237adc71128000012", "additional_parameters" : { "Port_one" : 2, "Port_two" : 4}},
             {"_id" : objectid.ObjectId("5010319237adc71128000007"), "connecting_resource" : "5010319237adc71128000013", "specification_name" : "NEW", "connected_resource" : "5010319237adc71128000011", "additional_parameters" : { "Port_one" : 5, "Port_two" : 6}}]

RESOURCE_LIST =[{"_id" : objectid.ObjectId("5010319237adc71128000001"), "specification_name" : "Switch", "res_status" : "standby", "owner" : "KST", "external_system" : "", "description" : "Portable computer of Konstantin Andrusenko", "additional_parameters" : {"Vendor" : "Apple", "model" : "MacBook Pro ", "memory" : 8192, "CPU" : "Intel Core i5"}},
                {"_id" : objectid.ObjectId("5010319237adc71128000002"), "specification_name" : "Switch", "res_status" : "standby", "owner" : "KST", "external_system" : "", "description" : "Portable computer of Konstantin Andrusenko", "additional_parameters" : {"Vendor" : "Apple", "model" : "MacBook Pro ", "memory" : 8192, "CPU" : "Intel Core i5"}},
                {"_id" : objectid.ObjectId("5010319237adc71128000666"), "specification_name" : "Switch", "res_status" : "down", "owner" : "Alex", "external_system" : "", "description" : "Portable computer of Aleksey Bogoslovskyi", "additional_parameters" : {"Vendor" : "Dell", "model" : "Vostro 1310", "memory" : 4096, "CPU" : "Intel Core2Duo T5670"}},
                {"_id" : objectid.ObjectId("5010319237adc71128000003"), "specification_name" : "Switch", "res_status" : "down", "owner" : "Alex", "external_system" : "", "description" : "Portable computer of Aleksey Bogoslovskyi", "additional_parameters" : {"Vendor" : "Dell", "model" : "Vostro 1310", "memory" : 4096, "CPU" : "Intel Core2Duo T5670"}},
                {"_id" : objectid.ObjectId("5010319237adc71128000004"), "specification_name" : "DSLAM", "res_status" : "down", "owner" : "Alex", "external_system" : "", "description" : "Portable computer of Aleksey Bogoslovskyi", "additional_parameters" : {"Vendor" : "Dell", "model" : "Vostro 1310", "memory" : 4096, "CPU" : "Intel Core2Duo T5670"}}]

SPEC_LIST = [{"_id" : objectid.ObjectId("5059769d6998cb10e2000000"), 'type_name': 'L2', 'connecting_type': 'Switch', 'connected_type': 'Switch', 'params_spec':{'param_name': 'test_param_2','param_type': 'string'}}]                

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
    insert_data(conn[DB_NAME][MongoDatabaseAPI.ET_CONNECTION], CONN_LIST)
    insert_data(conn[DB_NAME][MongoDatabaseAPI.ET_RESOURCE], RESOURCE_LIST)
    insert_data(conn[DB_NAME][MongoDatabaseAPI.ET_SPECIFICATION], SPEC_LIST)

    conn.disconnect()

class TestConnectionOperationalAPI(unittest.TestCase):
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

  def create_conn(self):
    update_conn1 = { "_id" : objectid.ObjectId("5010319237adc71128000000"), "specification_name" : "L3", "connecting_resource" : "5010319237adc71128000001", 
                      "connected_resource" : "5010319237adc71128000003","additional_parameters" : { "Port_one" : 10, "Port_two" : 30}}
    update_conn2 = { "_id" : objectid.ObjectId("5010319237adc71128000000"), "specification_name" : "L3", "connecting_resource" : "5010319237adc71128000001", 
                      "connected_resource" : "5010319237adc71128000003", "additional_parameters" : { "Port_one" : 24, "Port_two" : 30, 'new_name': 'new_value'}}

    return update_conn1, update_conn2

  def test_updateConnection(self):
    time.sleep(1)
    self.maxDiff = None
    res_spec = self.create_spec()
    Resource.setup_specification([res_spec])     

    conn_param = { 'param_name': 'test_param_2',
                     'param_type': 'string'}
    spec = ConnectionSpecification({'type_name': 'L3', 'connecting_type': 'Switch', 'connected_type': 'Switch'},
                                        params_spec = [conn_param])

    Connection.setup_specification([spec])
    connection = Connection()
    connection = ConnectionOperationalAPI('localhost', DB_NAME)

        #Specification <L4> is not registered!
    self.check_exception(lambda: connection.updateConnection('5010319237adc71128000000', 'L4', '5010319237adc71128000001', '5010319237adc71128000003'), BIException)
        #Specification <DSLAM> is not registered! device with _id 5010319237adc71128000004
    self.check_exception(lambda: connection.updateConnection('5010319237adc71128000000', 'L3', '5010319237adc71128000001', '5010319237adc71128000004'), BIException)

    raw_conn = connection.updateConnection('5010319237adc71128000000', 'L3', '5010319237adc71128000001', '5010319237adc71128000003')
    conn = raw_conn.to_dict()
    update_conn = self.create_conn()
    self.assertEqual(conn, update_conn[0])

    raw_conn = connection.updateConnection('5010319237adc71128000000', 'L3', '5010319237adc71128000001', '5010319237adc71128000003', additional_parameters={'Port_one': 24, 'new_name': 'new_value'})
    conn = raw_conn.to_dict()
    update_conn = self.create_conn()
    self.assertEqual(conn, update_conn[1])

    spec = ConnectionSpecification({'type_name': 'L2', 'connecting_type': 'Switch', 'connected_type': 'Access'},
                                        params_spec = [conn_param])
    Connection.setup_specification([spec])
        #Connected resource should be specified by <Access> specification!
    self.check_exception(lambda: connection.updateConnection('5010319237adc71128000000', 'L2', '5010319237adc71128000001', '5010319237adc71128000003'), BIValueError)

  def test_findConnection(self):
    time.sleep(1)
    connection = ConnectionOperationalAPI('localhost', DB_NAME)

    raw_conn = connection.findConnection({'specification_name__in': ['NEW', 'Test']})
    conn_list = []
    for item in raw_conn:
      new_conn = item.to_dict()
      conn_list.append(new_conn)

    self.assertEqual(3, len(conn_list))

  def test_connectResources(self):
    time.sleep(1)
    res_spec = self.create_spec()
    Resource.setup_specification([res_spec])   

    conn_param = { 'param_name': 'test_param_2',
                     'param_type': 'string'}
    spec = ConnectionSpecification({'type_name': 'L2', 'connecting_type': 'Switch', 'connected_type': 'Switch'},
                                        params_spec = [conn_param])

    Connection.setup_specification([spec])
    connection = Connection()

    connection = ConnectionOperationalAPI('localhost', DB_NAME)
        #Connection between similar resources is not allowed!
    self.check_exception(lambda: connection.connectResources('L2', '5010319237adc71128000666', '5010319237adc71128000666'), BIException)
        #Can't find information about record with entity_id 5010319237adc71128000100 in resource collection
    self.check_exception(lambda: connection.connectResources('L2', '5010319237adc71128000666', '5010319237adc71128000100'), BIException)
        #connectResources() takes exactly 4 arguments (3 given)
    self.check_exception(lambda: connection.connectResources('L2', '5010319237adc71128000666'), Exception)
        #Specification <L3> is not registered!
    self.check_exception(lambda: connection.connectResources('L3', '5010319237adc71128000666', '5010319237adc71128000003'), BIException)

    connection.connectResources('L2', '5010319237adc71128000666', '5010319237adc71128000003', Port_one={'id':9}, Port_two={'id':10})
    connection.connectResources('L2', '5010319237adc71128000666', '5010319237adc71128000002')

    self.db_conn = MongoDatabaseAPI('localhost',DB_NAME)  
    self.db_conn.connect()
    find_conn = self.db_conn.find_entities('connection', {'connecting_resource': '5010319237adc71128000666'})
    self.db_conn.close()

    self.assertEqual(2, len(find_conn))

      #Connection between resources "5010319237adc71128000666" and "5010319237adc71128000003" by type "L2" already exist!
    self.check_exception(lambda: connection.connectResources('L2', '5010319237adc71128000666', '5010319237adc71128000003'), BIException)

  def test_disconnectResourcesById(self):
    time.sleep(1)
    connection = ConnectionOperationalAPI('localhost', DB_NAME)

    connection.disconnectResourcesById('5010319237adc71128000000')
    self.db_conn = MongoDatabaseAPI('localhost', DB_NAME)
    self.db_conn.connect()

      #Can't find information about record with entity_id 5010319237adc71128000006 in connection collection
    self.check_exception(lambda: self.db_conn.get_entity('connection','5010319237adc71128000000'), BIValueError)
    self.db_conn.close()

  def test_disconnectResources(self):
    connection = ConnectionOperationalAPI('localhost', DB_NAME)
      #disconnect connect with _id = 5010319237adc71128000006
    connection.disconnectResources('L2','5010319237adc71128000001', '5010319237adc71128000002')

    self.db_conn = MongoDatabaseAPI('localhost', DB_NAME)
    self.db_conn.connect()
      #Can't find information about record with entity_id 5010319237adc71128000006 in connection collection
    self.check_exception(lambda: self.db_conn.get_entity('connection','5010319237adc71128000000'), BIValueError)
    self.db_conn.close()

  def test_getLinkedResources(self):
    time.sleep(1)
    connection = ConnectionOperationalAPI('localhost', DB_NAME)

    raw_conn = connection.getLinkedResources("5010319237adc71128000011", 'NEW', 'connecting_resource')
    conn_list = []
    for item in raw_conn:
      new_conn = item.to_dict()
      conn_list.append(new_conn)

    raw_conn = connection.getLinkedResources("5010319237adc71128000011", 'NEW')
    for item in raw_conn:
      new_conn = item.to_dict()
      conn_list.append(new_conn)

    self.assertEqual(3, len(conn_list))

      # Connection directions "test" is not correct!
    self.check_exception(lambda: connection.getLinkedResources("5010319237adc71128000011", 'NEW', 'test'),BIException)

if __name__ == '__main__':
    unittest.main()