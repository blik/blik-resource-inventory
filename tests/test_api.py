import unittest
from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
from blik.inventory.api.connection_oper_api import ConnectionOperationalAPI
from blik.inventory.core.base_entities import *

class TestResourceOperationalAPI(unittest.TestCase):
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
    def create_resources(self):
        test_res = {'description': None, 
                    'additional_parameters': {'_id': None},
                    'specification_name': 'Access', 
                    'resource_status': 'Active', 
                    'owner': None, 
                    'location': None, 
                    'department': None, 
                    'external_system': None}

        test_res_2 = {'description': 'description Acces device', 
                    'additional_parameters': {'_id': None,
                                              'additional_parameters': {'add_param': 'add_value',
                                                                        'add_param_2': 'add_value_2'}},
                    'specification_name': 'Access', 
                    'resource_status': 'New', 
                    'owner': 'test owner', 
                    'location': 'test location', 
                    'department': 'test department', 
                    'external_system': 'test external system'}

        updated_resource = {'owner': 'test owner', 
                            'description': 'update description PE device', 
                            'additional_parameters': {'additional_parameters': {'add_param': 'add_value',
                                                                                'add_param_2': 'add_value_2'}},
                            'department': 'test department',
                            'external_system': 'update external system',
                            'specification_name': 'Access',
                            'resource_status': 'Closed',
                            'location': 'test location'}    

        return test_res, test_res_2, updated_resource

    def create_spec(self):
        child_param_1 = {'param_name': 'add_param',
                     'param_type': 'string',
                     'description': 'Child parameter #1',
                     'mandatory': False}

        param_1 = { 'param_name': 'additional_parameters',
                     'param_type': 'to_dict',
                     'description': 'Test parameter #1',
                     'mandatory': False,
                     #'possible_values': ['add_value'],
                     'default_value': 'default add value',
                     'children_spec': [child_param_1]}

        #param_2 = { 'param_name': 'test_param_2',
        #             'param_type': 'list',
        #             'description': 'Test parameter #2',
        #             'mandatory': True,
        #             'children_spec': [child_param_1]}

        spec = ResourceSpecification({'type_name': 'Access'}, params_spec = [param_1])
        return spec

    def test_create_resources(self):
        resources = self.create_resources()
        specs = self.create_spec()
        Resource.setup_specification([specs])

        resource = ResourceOperationalAPI('db_conn')

        raw_resource = resource.createResource('Access', 'Active', 'Test DSLAM device')        
        self.check_exception(lambda: self.assertEqual(resources[0], raw_resource.to_dict()), AssertionError)

        self.check_exception(lambda: resource.createResource('Access'), TypeError)

        raw_resource = resource.createResource('Access', 'Active')
        self.assertEqual(resources[0], raw_resource.to_dict())

        raw_resource = resource.createResource('Access', 'New', 'description Acces device', 'test external system', 'test location', 'test department', 'test owner',
                                                additional_parameters={'add_param': 'add_value', 'add_param_2': 'add_value_2'})
        self.assertEqual(resources[1], raw_resource.to_dict())

    def test_updateResource(self):
        resources = self.create_resources()
        specs = self.create_spec()
        Resource.setup_specification([specs])

        resource = ResourceOperationalAPI('db_conn')
        self.check_exception(lambda: resource.updateResource(), TypeError)

        raw_resource = resource.updateResource(1, 'Closed', 'update description PE device', 'update external system')
                                                #additional_parameters={'add_param': 'add_value', 'add_param_2': 'add_value_2'})
        self.assertEqual(resources[2], raw_resource.to_dict())




if __name__ == '__main__':
    unittest.main()