
import unittest
from blik.inventory.core.base_entities import *

def check_exception(routine, exception=BIException):
    try:
        routine()
    except exception:
        pass
    except Exception, err:
        raise Exception('Exception <%s> is not expected in this case! Exception details: %s'% \
                            (err.__class__.__name__, err))
    else:
        raise Exception('Should be raised exception in this case')


class TestBaseEntities(unittest.TestCase):
    def create_test_res_spec(self):
        param_1 = { 'param_name': 'test_param_1',
                     'param_type': 'integer',
                     'description': 'Test parameter #1',
                     'mandatory': False,
                     'possible_values': [1,2,3,4,5,6,7,8,9,0],
                     'default_value': 0}

        child_param_1 = {'param_name': 'child_param_1',
                     'param_type': 'string',
                     'description': 'Child parameter #1',
                     'mandatory': True}

        param_2 = { 'param_name': 'test_param_2',
                     'param_type': 'list',
                     'description': 'Test parameter #2',
                     'mandatory': True,
                     'children_spec': [child_param_1]}

        spec = ResourceSpecification({'type_name': 'TestSpec'}, params_spec = [param_1, param_2])

        return spec

    def test_resource_spec(self):
        check_exception(lambda: ResourceSpecification())
        check_exception(lambda: ResourceSpecification(1, 2))
        check_exception(lambda: ResourceSpecification(1), BIValueError)

        spec = self.create_test_res_spec()
        self.assertEqual(spec.type_name(), 'TestSpec')

        spec.validate()
        spec.validate_entity({'test_param_2': [{'child_param_1': 'test1'}, {'child_param_1': 'test2'}]})

        check_exception(lambda: spec.validate_entity({'test_param_2':[], 'test_param_1': 'test'}), BIValueError)
        check_exception(lambda: spec.validate_entity({'test_param_2':[], 'test_param_1': '12'}), BIValueError)
        check_exception(lambda: spec.validate_entity({'test_param_2':[1,2,3,4]}), BIValueError)
        check_exception(lambda: spec.validate_entity({'test_param_2':[{'fake_param':1}]}), BIValueError)
        check_exception(lambda: spec.validate_entity({'test_param_2':[], 'fake_param': '222'}), BIValueError)
        check_exception(lambda: spec.validate_entity({'test_param_1': 1}), BIValueError)

        bad_param = {'param_name': 'fake'}
        spec = ResourceSpecification({'type_name': 'TestSpec2', 'params_spec': [bad_param]})
        check_exception(lambda: spec.validate(), BIValueError)

        bad_param = {'param_name': 'fake', 'param_type': 'fake'}
        spec = ResourceSpecification({'type_name': 'TestSpec2', 'params_spec': [bad_param]})
        check_exception(lambda: spec.validate(), BIValueError)

        bad_param = {'param_name': 'fake', 'param_type': 'integer', 'possible_values':[1,2,3], 'default_value': 0}
        spec = ResourceSpecification({'type_name': 'TestSpec2', 'params_spec': [bad_param]})
        check_exception(lambda: spec.validate(), BIValueError)

        child_param_1 = {'param_name': 'child_param_1',
                     'param_type': 'typo_string',
                     'description': 'Child parameter #1',
                     'mandatory': True}
        bad_param = {'param_name': 'fake', 'param_type': 'dict', 'children_spec': [child_param_1]}
        spec = ResourceSpecification({'type_name': 'TestSpec2', 'params_spec': [bad_param]})
        check_exception(lambda: spec.validate(), BIValueError)

        child_param_1['param_type'] = 'integer'
        bad_param = {'param_name': 'fake', 'param_type': 'dict', 'children_spec': [child_param_1]}
        spec = ResourceSpecification({'type_name': 'TestSpec2', 'params_spec': [bad_param]})
        self.assertEqual(spec.type_name(), 'TestSpec2')

        spec.validate()
        spec.validate_entity({'fake': {'child_param_1': '23'}})
        check_exception(lambda: spec.validate_entity({'fake': {'child_param_1': '33ee'}}), BIValueError)

        ret_value = spec.to_dict()
        self.assertTrue(isinstance(ret_value, dict))
        self.assertEqual(ret_value['params_spec'][0], bad_param)

    def test_collection_spec(self):
        param_1 = { 'param_name': 'test_param_1',
                     'param_type': 'integer'}

        param_2 = { 'param_name': 'test_param_2',
                     'param_type': 'string'}

        test_allowed_types = ['test_res1', 'test_res2']
        spec = CollectionSpecification({'type_name': 'TestCollectionSpec'}, allowed_types=test_allowed_types, params_spec = [param_1, param_2])
        self.assertEqual(spec.type_name(), 'TestCollectionSpec')
        spec.validate()

        allowed_types = spec.get_allowed_types()
        self.assertEqual(allowed_types, test_allowed_types)

        spec = CollectionSpecification({'type_name': 'TestCollectionSpec'}, params_spec = [param_1, param_2])
        check_exception(lambda: spec.validate(), BIValueError)


    def test_connection_spec(self):
        conn_param = { 'param_name': 'test_param_2',
                     'param_type': 'string'}

        spec = ConnectionSpecification({'type_name': 'TestConnectionSpec'})
        check_exception(lambda: spec.validate(), BIValueError)

        spec = ConnectionSpecification({'type_name': 'TestConnectionSpec', 'connecting_type': 'testRes1'}, params_spec = [conn_param])
        check_exception(lambda: spec.validate(), BIValueError)

        spec = ConnectionSpecification({'type_name': 'TestConnectionSpec', 'connecting_type': 'testRes1', 'connected_type': 'testRes2'},
                                        params_spec = [conn_param])
        spec.validate()
        connecting, connected = spec.get_connectors_types()
        self.assertEqual(connecting, 'testRes1')
        self.assertEqual(connected, 'testRes2')

    def test_resource_entity(self):
        res = Resource()
        check_exception(lambda: res.validate())

        res = Resource(specification_name='TestSpec')
        check_exception(lambda: res.validate(), BIValueError)

        spec = self.create_test_res_spec()
        Resource.setup_specification([spec])

        res = Resource(some_attr=1)
        check_exception(lambda: res.validate(), BIValueError)

        res = Resource(specification_name='TestSpec')
        check_exception(lambda: res.validate(), BIValueError)

        res = Resource(specification_name='TestSpec', resource_status='new', additional_parameters='fake')
        check_exception(lambda: res.validate(), BIValueError)

        add_params = {}
        res = Resource(specification_name='TestSpec', resource_status='new', additional_parameters=add_params)
        check_exception(lambda: res.validate(), BIValueError)

        add_params = {'test_param_2': [{'child_param_1': 'test1'}, {'child_param_1': 'test2'}]}
        res = Resource(specification_name='TestSpec', resource_status='new', additional_parameters=add_params)
        res.validate()

        status = res.get_resource_status()
        self.assertEqual(status, 'new')

        status = res.get_status()
        self.assertEqual(status, NOT_FOUND)

    def test_collection_entity(self):
        collection = Collection()
        check_exception(lambda: collection.validate())

        param_1 = { 'param_name': 'test_param_1',
                     'param_type': 'integer'}
        test_allowed_types = ['TestSpec', 'SomeOtherType']
        spec = CollectionSpecification({'type_name': 'TestCollectionSpec'}, allowed_types=test_allowed_types, params_spec = [param_1])
        spec.validate()

        Collection.setup_specification([spec])
        collection = Collection({'specification_name': 'TestCollectionSpec'})
        collection.set_test_param_1(10)
        collection.validate()

        check_exception(lambda: collection.append_resource('fake'), BIValueError)

        res = Resource(specification_name='SomeFakeSpec')
        check_exception(lambda: collection.append_resource(res), BIValueError)

        spec = self.create_test_res_spec()
        Resource.setup_specification([spec])

        add_params = {'test_param_2': [{'child_param_1': 'test1'}, {'child_param_1': 'test2'}]}
        res = Resource(specification_name='TestSpec', resource_status='new', additional_parameters=add_params)
        res.validate()

        check_exception(lambda: collection.append_resource(res))

        res.set__id(666)
        collection.append_resource(res)
        res_list = collection.get_resources()
        self.assertEqual(res_list, [666])

    def test_connection_entity(self):
        connection = Connection()
        check_exception(lambda: connection.validate())

        conn_param = { 'param_name': 'test_param_2',
                     'param_type': 'string'}

        spec = ConnectionSpecification({'type_name': 'TestConnectionSpec', 'connecting_type': 'TestSpec', 'connected_type': 'TestSpec'},
                                        params_spec = [conn_param])
        spec.validate()

        Connection.setup_specification([spec])
        conn = Connection(specification_name='TestConnectionSpec')
        check_exception(lambda: conn.validate())
        conn.set_test_param_2(22)
        conn.validate()

        spec = self.create_test_res_spec()
        Resource.setup_specification([spec])

        add_params = {'test_param_2': [{'child_param_1': 'test1'}, {'child_param_1': 'test2'}]}
        res1 = Resource(specification_name='TestSpec', resource_status='new', additional_parameters=add_params)
        res1.validate()

        add_params = {'test_param_2': [{'child_param_1': 'some_value'}]}
        res2 = Resource(specification_name='TestSpec', resource_status='active', additional_parameters=add_params)
        res2.validate()

        fake_res = Resource(specification_name='FakeSpec')

        check_exception(lambda: conn.connect(fake_res, res2), BIValueError)
        check_exception(lambda: conn.connect('fake', res2), BIValueError)
        check_exception(lambda: conn.connect(res1, 'fake2'), BIValueError)
        check_exception(lambda: conn.connect(res1, res2))

        res1.set__id(123)
        res2.set__id(321)
        conn.connect(res1, res2)
        r_res1 = conn.get_connecting_resource()
        r_res2 = conn.get_connected_resource()
        self.assertEqual(r_res1, 123)
        self.assertEqual(r_res2, 321)

if __name__ == '__main__':
    unittest.main()

