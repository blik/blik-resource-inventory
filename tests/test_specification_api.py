from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
from blik.inventory.api.connection_oper_api import ConnectionOperationalAPI
from blik.inventory.api.management_api import ManagementAPI
from blik.inventory.core.base_entities import *
from blik.inventory.backend.common import *
from blik.inventory.backend.mongo import  MongoDatabaseAPI

import time
import unittest
from pymongo import objectid

DB_NAME = 'Test_BlikRI'
CONN_STRING = 'localhost:27017'

SPEC_LIST = [{"_id" : objectid.ObjectId("5059769d6998cb10e2000222"), "spec_type" : "connection", 'type_name': 'L2', 'connecting_type': 'Switch', 'connected_type': 'Switch', 'params_spec':{'param_name': 'test_param_2','param_type': 'string'}},
            { "_id" : objectid.ObjectId("5059769d6998cb10e2000111"), "params_spec" : [{ "param_name" : "interfaces", "param_type" : "dict", "description": "Specify interface for Switch",  "children_spec" :[{"param_name" : "idx", "param_type" : "integer",}]},  {"param_name" : "board", "param_type" : "integer" }], 
                            "type_name" : "Switch", "spec_type" : "resource", "parent_type_name" : "Parent Switch" },
            {"_id" : objectid.ObjectId("5059769d6998cb10e2000333"), "spec_type" : "collection", 'type_name': 'L2VPN_site', 'allowed_types': ['Access', 'Switch'], 'params_spec':{'param_name': 'test_param_2','param_type': 'string'}},
            {"_id" : objectid.ObjectId("5059769d6998cb10e2000444"), "spec_type" : "some spec", 'type_name': 'L2VPN_site', 'allowed_types': ['Access', 'Switch'], 'params_spec':{'param_name': 'test_param_2','param_type': 'string'}}]                

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

  def get_spec(self):
    spec_res_1 = {'params_spec': [{'param_name': 'UPDATE_interfaces', 'param_type': 'dict', 'children_spec': [{'param_name': 'UPDATE_idx', 'param_type': 'integer','mandatory': True}]}, 
                                  {'param_name': 'UPDATE_board', 'param_type': 'integer'}, 
                                  {'param_name': 'new_value', 'param_type': 'string'}],
                 'type_name': 'Switch', '_id': objectid.ObjectId('5059769d6998cb10e2000111'), 'spec_type': 'resource', 'parent_type_name': 'Parent Switch update', 'description': 'description'}

    spec_conn_1 = {'type_name': 'L3', 'parent_type_name': 'UPDATED Parent', 'connecting_type': 'Access', 'spec_type': 'connection', 'description':'description', '_id': objectid.ObjectId('5059769d6998cb10e2000222'), 'connected_type': 'Switch',
                  'params_spec': [{'param_name': 'id', 'param_type': 'integer'}, 
                                {'param_name': 'UPDATE_interfaces', 'param_type': 'dict', 'children_spec': [{'param_name': 'UPDATE_idx', 'param_type': 'integer', 'mandatory': True}]}]}

    spec_coll_1 = {'allowed_types': ['Access', 'Switch', 'DSLAM'], 'type_name': 'L3VPN_site', 'parent_type_name': 'UPDATED Parent', 'spec_type': 'collection', 'description':'description', '_id': objectid.ObjectId('5059769d6998cb10e2000333'),
                 'params_spec': [{'param_name': 'id', 'param_type': 'integer'}, 
                                {'param_name': 'UPDATE_interfaces', 'param_type': 'dict', 'children_spec': [{'param_name': 'UPDATE_idx', 'param_type': 'integer','mandatory': True}]}]}

    spec_res_2 = {u'params_spec': [{u'param_name': u'interfaces', u'description': u'Specify interface for Switch', u'param_type': u'dict', u'children_spec': [{u'param_name': u'idx', u'param_type': u'integer'}]}, {u'param_name': u'board', u'param_type': u'integer'}],
                  u'type_name': u'Switch', u'_id': '5059769d6998cb10e2000111', u'spec_type': u'resource', u'parent_type_name': u'Parent Switch'}

    return spec_res_1, spec_conn_1, spec_coll_1, spec_res_2

  def test_createSpecification(self):
    spec = ManagementAPI()

    child_param_1 = {'param_name': 'idx',
                     'param_type': 'integer',
                     'description': 'interface parameter',
                     'mandatory': True}
    param_1 = { 'param_name': 'interfaces',
                     'param_type': 'dict',
                     'description': 'Specify interface for Switch',
                     'mandatory': True,
                     'possible_values': ['add_value','ww'],
                     'default_value': 'add_value',
                     'children_spec': [child_param_1]}
    param_2 = { 'param_name': 'board',
                     'param_type': 'integer',
                     'description': '',
                     'mandatory': True,
                     'possible_values': [1,2,3,4,5,6,7],
                     'default_value': 1}

    param_conn = {'param_name': 'id',
                  'param_type': 'integer'}

    param_coll = {'param_name': 'id',
                  'param_type': 'integer'}

    #Specification type <wrong_type> is not supported!
    self.check_exception(lambda:  spec.createSpecification('Switch', 'Parent Switch', 'wrong_type', 'description', params_spec=[param_1]), BIException)

    spec_res = spec.createSpecification('Switch', 'Parent Switch', 'resource', 'description', params_spec=[param_1, param_2])
    
    spec_conn = spec.createSpecification('L2', 'Parent L2', 'connection', 'description', connecting_type='Access', connected_type='Switch', params_spec=[param_conn])

    spec_coll = spec.createSpecification('l2vpn_site', 'Parent', 'collection', 'description', allowed_types=['Access', 'Switch'], params_spec=[param_coll])

  def test_updateSpecification(self):
    time.sleep(1)
    spec = ManagementAPI()

    child_param_1 = {'param_name': 'UPDATE_idx',
                     'param_type': 'integer',
                     'mandatory': True}
    param_1 = { 'param_name': 'UPDATE_interfaces',
                     'param_type': 'dict',
                     'children_spec': [child_param_1]}
    param_2 = { 'param_name': 'UPDATE_board',
                'param_type': 'integer'}

    param_3 = {'param_name': 'new_value',
                'param_type': 'string'}

    param_conn = {'param_name': 'id',
                  'param_type': 'integer'}

    #Specification type <some name> is not supported!
    self.check_exception(lambda:  spec.updateSpecification('5059769d6998cb10e2000111','Switch', 'Parent Switch update', 'some name', 'description', params_spec=[param_1]), BIException)

    spec_res = spec.updateSpecification('5059769d6998cb10e2000111','Switch', 'Parent Switch update', 'resource', 'description', params_spec=[param_1, param_2, param_3]).to_dict()
    update_spec_res = self.get_spec()
    self.assertEqual(spec_res, update_spec_res[0])

    spec_conn = spec.updateSpecification('5059769d6998cb10e2000222','L3', 'UPDATED Parent', 'connection', 'description', connecting_type='Access', connected_type='Switch', params_spec=[param_conn,param_1]).to_dict()
    update_spec_res = self.get_spec()
    self.assertEqual(spec_conn, update_spec_res[1])

    spec_coll = spec.updateSpecification('5059769d6998cb10e2000333','L3VPN_site', 'UPDATED Parent', 'collection', 'description', allowed_types=['Access','Switch','DSLAM'], params_spec=[param_conn,param_1]).to_dict()
    update_spec_res = self.get_spec()
    self.assertEqual(spec_coll, update_spec_res[2])

  def test_findSpecification(self):
    time.sleep(1)
    spec = ManagementAPI()
    filter_coll = {'type_name': 'L2VPN_site'}

    spec_coll = spec.findSpecification('collection', filter_coll)
    self.assertEqual(2, len(spec_coll))

  def test_getSpecification(self):
    time.sleep(1)
    spec = ManagementAPI()

    #Specification type <some spec> is not supported!
    self.check_exception(lambda:  spec.getSpecification('5059769d6998cb10e2000444'), BIException)

    spec_res = spec.getSpecification('5059769d6998cb10e2000111').to_dict()
    get_spec_res = self.get_spec()
    self.assertEqual(spec_res, get_spec_res[3])

  def test_deleteSpecification(self):
    time.sleep(1)
    spec = ManagementAPI()
    self.db_conn = MongoDatabaseAPI('localhost',DB_NAME)
    self.db_conn.connect()

    spec.deleteSpecification('5059769d6998cb10e2000111')

    #Can't find information about record with entity_id 5059769d6998cb10e2000111 in resource collection
    self.check_exception(lambda: self.db_conn.get_entity('resource', '5059769d6998cb10e2000111'), BIException)

if __name__ == '__main__':
  unittest.main()