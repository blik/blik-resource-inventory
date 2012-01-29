
import unittest
#from blik.inventory.core.base_entities import *
from base_entities import *


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
    def test_resource_spec(self):
        check_exception(lambda: ResourceSpecification())
        check_exception(lambda: ResourceSpecification(1, 2))
        check_exception(lambda: ResourceSpecification(1), BIValueError)

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

        child_param_1['param_type'] = 'typo_integer'
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


if __name__ == '__main__':
    unittest.main()

