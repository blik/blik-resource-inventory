#!/usr/bin/python
#pylint: disable-msg=C0301
"""
Purpose: Implementation of base entities of Resource Inventory
Created: 22.01.2012
Author:  Konstantin Andrusenko
"""

from inv_exceptions import BIException, BIValueError

NOT_FOUND = None

class ParameterSpecification:
    '''Specification of entity parameter'''

    #parameter types
    PT_INTEGER = 'integer'
    PT_STRING = 'string'
    PT_OID = 'oid'
    PT_LIST = 'list'
    PT_DICT = 'dict'

    POSSIBLE_TYPES = ['integer', 'string', 'oid', 'list', 'dict']
    ATTRS = ['param_name', 'param_type', 'mandatory', 'possible_values', 'default_value', 'description', 'children_spec']

    def __init__(self, *args, **kwargs):
        '''Constructor
        *args - you can put dict parameter as no-named parameter
        **kwargs - key-value attributes
        '''
        if args:
            if len(args) != 1:
                raise BIException('Constructor of <%s> expect one no-named parameter only!'%
                                    self.__class__.__name__)

            params_dict = args[0]
            if not isinstance(params_dict, dict):
                raise BIValueError('ParameterSpecification expect dictionary as input parameter!')
        else:
            params_dict = {}

        params_dict.update(kwargs)

        for item in params_dict:
            if item not in self.ATTRS:
                raise BIValueError('Attribute <%s> is not expected for %s'%(item, self.__class__.__name__))

        self.param_name = params_dict.get('param_name', None)
        self.param_type = params_dict.get('param_type', None)
        self.mandatory = params_dict.get('mandatory', True)
        self.possible_values = params_dict.get('possible_values', None)
        self.default_value = params_dict.get('default_value', None)
        self.description = params_dict.get('description', None)
        self.children_spec = {}
        children = params_dict.get('children_spec', [])

        for child in children:
            spec = ParameterSpecification(child)
            self.children_spec[spec.param_name] = spec

    def validate(self):
        '''Validate specification parameters'''
        if self.param_type not in ParameterSpecification.POSSIBLE_TYPES:
            raise BIValueError('Parameter type "%s" is not supported!'% self.param_type)

        if not self.param_name:
            raise BIValueError('Parameter name is not specified!')

        if self.possible_values and (self.default_value is not None) and (self.default_value not in self.possible_values):
            raise BIValueError('Default value should be listed in possible values list!')

        for child in self.children_spec.values():
            child.validate()

    def to_dict(self):
        '''Return specification as dict'''
        ret_dict = { 'param_name': self.param_name,
                     'param_type': self.param_type,
                     'description': self.description,
                     'mandatory': self.mandatory }

        if self.possible_values:
            ret_dict['possible_values'] = self.possible_values
        if self.default_value:
            ret_dict['default_value'] = self.default_value

        if self.children_spec:
            ret_dict['children_spec'] = []
            for child in self.children_spec.values():
                ret_dict['children_spec'].append(child.to_dict())

        return ret_dict

    def is_mandatory(self):
        '''return parameter mandatory flag'''
        return self.mandatory

    def validate_value(self, value):
        '''Validate @value in accordance to specification'''
        if value is None:
            #value is NULL, validation skipping...
            return

        #check value type
        if self.param_type == ParameterSpecification.PT_INTEGER:
            try:
                value = int(value)
            except ValueError:
                raise BIValueError('Parameter "%s" should has integer value, but "%s" occured!'%(self.param_name, value))
        elif self.param_type == ParameterSpecification.PT_STRING:
            value = str(value)
        elif self.param_type == ParameterSpecification.PT_OID:
            raise BIValueError('Validation of OID type is not implemented')
        elif self.param_type == ParameterSpecification.PT_LIST:
            if value.__class__ != list:
                raise BIValueError('Parameter "%s" should be list, but "%s" occured!'%(self.param_name, value))
        elif self.param_type == ParameterSpecification.PT_DICT:
            if value.__class__ != dict:
                raise BIValueError('Parameter "%s" should be dict, but "%s" occured!'%(self.param_name, value))

        if self.possible_values and (str(value) not in self.possible_values):
            raise BIValueError('Value "%s" are not allowed for parameter "%s". Check possible values for this parameter'%\
                            (value, self.possible_values))

        return value


#-------------------------------------------------------------------------------------------------------------


class BaseSpecification:
    '''Specification of resource, connection and collection'''
    SPEC_TYPE = 'base'

    def __init__(self, *args, **kwargs):
        '''Constructor
        *args - you can put parameters dict as no-named parameter
        **kwargs - key-value attributes
        '''
        if (not args) and (not kwargs):
            raise BIException('Constructor of <%s> expect *args or **kwargs parameters'%
                                self.__class__.__name__)

        if args:
            if len(args) != 1:
                raise BIException('Constructor of <%s> expect one no-named parameter only!'%
                                    self.__class__.__name__)
            params_dict = args[0]
            if not isinstance(params_dict, dict):
                raise BIValueError('BaseSpecification expect dictionary as input parameter!')
        else:
            params_dict = {}

        params_dict.update(kwargs)

        self.params_dict = params_dict
        self.parent_spec = None

    def set_parent_specification(self, parent_spec):
        '''setup parent specification object'''
        if not isinstance(parent_spec, BaseSpecification):
            raise BIValueError('Parent specification should has BaseSpecification type')

        t_name = parent_spec.type_name()
        parent_t_name = self.parent_type_name()
        if t_name != parent_t_name:
            raise BIValueError('<%s> type specification expected as parent specification!' % parent_t_name)

        self.parent_spec = parent_spec

    def set__id(self, spec_id):
        '''setup specification ID'''
        self.params_dict['__id'] = spec_id

    def to_dict(self):
        '''return specification as dict'''
        return self.params_dict

    def type_name(self):
        return self.params_dict.get('type_name', None)

    def parent_type_name(self):
        return self.params_dict.get('parent_type_name', None)

    def get_params_spec(self):
        '''Get parameters specifications dict'''
        ret_dict = {}
        if self.parent_spec:
            ret_dict.update(self.parent_spec.get_params_spec())

        specs = self.params_dict.get('params_spec', [])

        for spec_item in specs:
            spec = ParameterSpecification(spec_item)
            ret_dict[spec.param_name] = spec

        return ret_dict

    def is_inherit(self, type_name):
        if self.type_name() == type_name:
            return True

        if self.parent_spec:
            return self.parent_spec.is_inherit(type_name)

        return False

    def validate(self):
        '''Validate base specification parameters'''
        if not self.params_dict.get('type_name', None):
            raise BIValueError('Type name is not specified!')

        spec_type = self.params_dict.get('spec_type', self.SPEC_TYPE)
        if spec_type != self.SPEC_TYPE:
            raise BIValueError('<%s> specification type expected, but <%s> occured!'% (self.SPEC_TYPE, spec_type))

        if not self.params_dict.get('params_spec', None):
            raise BIValueError('Parameter specifications is not found for "%s"!'% self.type_name())

        for param_spec in self.params_dict['params_spec']:
            ParameterSpecification(param_spec).validate()

    def get_indexes(self):
        '''Get information about entity's indexes'''
        raise Exception('This method is not implemented')

    def validate_entity(self, params_dict, specs=None):
        '''Validate entity in accordance to specification'''
        if not isinstance(params_dict, dict):
            raise BIValueError('@params_dict should has a dictionary type!')

        if specs == None:
            params_spec_map = self.get_params_spec()
        else:
            params_spec_map = specs

        for spec_item in params_spec_map.values():
            if spec_item.is_mandatory() and (spec_item.param_name not in params_dict):
                raise BIValueError('Parameter "%s" is expected for "%s" entity type!'% \
                                                (spec_item.param_name, self.type_name()))

        for key, value in params_dict.items():
            param_spec = params_spec_map.get(key, None)
            if not param_spec:
                raise BIValueError('Parameter "%s" is not expected for "%s" entity type!'% (key, self.type_name()))

            param_spec.validate_value(value)
            if not value:
                continue

            if param_spec.param_type == param_spec.PT_LIST:
                for item in value:
                    self.validate_entity(item, param_spec.children_spec)

            if param_spec.param_type == param_spec.PT_DICT:
                self.validate_entity(value, param_spec.children_spec)


class ResourceSpecification(BaseSpecification):
    SPEC_TYPE = 'resource'

class CollectionSpecification(BaseSpecification):
    SPEC_TYPE = 'collection'

    def validate(self):
        '''Validate collection specification parameters'''
        BaseSpecification.validate(self)

        if not self.params_dict.get('allowed_types', None):
            raise BIValueError('Allowed resources types for collection "%s" is not specified!'%
                                self.type_name())

    def get_allowed_types(self):
        '''returns list of allowed resource types'''
        return self.params_dict['allowed_types']


class ConnectionSpecification(BaseSpecification):
    SPEC_TYPE = 'connection'

    def validate(self):
        '''Validate connection specification parameters'''
        BaseSpecification.validate(self)

        if not self.params_dict.get('connecting_type', None):
            raise BIValueError('Connecting resource type is not specified for connection "%s"!'%
                                self.type_name())

        if not self.params_dict.get('connected_type', None):
            raise BIValueError('Connected resource type is not specified for connection "%s"!'%
                                self.type_name())

    def get_connectors_types(self):
        '''return connecting and connected resource types'''
        return self.params_dict['connecting_type'], self.params_dict['connected_type']


#-------------------------------------------------------------------------------------------------------------


class BaseEntity:
    '''
    This class incapsulate base entity attributes and operations
    (same for resource, connection, collection...)
    '''

    SPECIFICATIONS = {}

    @classmethod
    def setup_specification(cls, spec_list):
        '''Setup list of resources specifications'''
        for spec in spec_list:
            if not isinstance(spec, BaseSpecification):
                raise Exception('Specification should be an object of BaseSpecification')

            cls.SPECIFICATIONS[spec.type_name()] = spec

    def __init__(self, *args, **kwargs):
        '''Constructor
        *args - you can put parameters dict as no-named parameter
        **kwargs - key-value attributes
        '''
        self._base_attributes = ['_id', 'specification_name', 'additional_parameters',
                                    'description', 'create_date', 'mod_date'] #should be extended in inherited class
        if args:
            if len(args) != 1:
                raise Exception('Constructor of <%s> expect one no-named parameter only!'%
                                    self.__class__.__name__)
            params_dict = args[0]

            if not isinstance(params_dict, dict):
                raise BIValueError('ParameterSpecification expect dictionary as input parameter!')
        else:
            params_dict = {}

        params_dict.update(kwargs)

        self.params_dict = params_dict
        self.additional_parameters = params_dict.get('additional_parameters', {})

    def specification(self):
        '''return entity specification'''
        spec_name = self.get_specification_name()
        spec = self.SPECIFICATIONS.get(spec_name, None)
        if spec is None:
            raise BIException('Specification <%s> is not registered!'% (spec_name))

        return spec

    def instance_of(self, type_name):
        return self.specification().is_inherit(type_name)

    def operations_help(self):
        '''return help string with get/set operations'''
        help_s = 'get_attribute(attr_name, default_value=None)\n'
        help_s += 'set_attribute(attr_name, value)\n'

        parameters = self.params_dict.keys() + self.additional_parameters.keys()
        for param_name in parameters:
            help_s += 'get_%s(default_value=NOT_FOUND)\n'% param_name
            help_s += 'set_%s(value)\n'% param_name

        return help_s

    def __get_attribute(self, attr_name, default_value=None):
        '''return value of @attr_name attribute of entity'''
        if attr_name in self._base_attributes:
            value = self.params_dict.get(attr_name, default_value)
        else:
            value = self.additional_parameters.get(attr_name, default_value)

        return value

    def __set_attribute(self, attr_name, attr_value):
        '''set value of @attr_name attribute of entity'''
        if attr_name in self._base_attributes:
            self.params_dict[attr_name] = attr_value
        else:
            self.additional_parameters[attr_name] = attr_value

    def __get_attribute_gen(self, attr_name):
        '''return function that returns value of attribute of entity'''
        def func(default_value=NOT_FOUND):
            return self.__get_attribute(attr_name, default_value)
        return func

    def __set_attribute_gen(self, attr_name):
        '''return function that sets value of attribute of entity'''
        def func(attr_value):
            self.__set_attribute(attr_name, attr_value)
        return func

    def __getattr__(self, attr_name):
        '''get/set operation for entity incapsulation'''

        if attr_name == 'get_attribute':
            return self.__get_attribute

        elif attr_name == 'set_attribute':
            return self.__set_attribute

        elif attr_name.startswith('get_'):
            return self.__get_attribute_gen(attr_name[4:])

        elif attr_name.startswith('set_'):
            return self.__set_attribute_gen(attr_name[4:])

    def to_dict(self):
        '''return entity attributes as dict'''
        self.params_dict['additional_parameters'] = self.additional_parameters
            
        return self.params_dict

    def validate(self):
        '''Validate entity attributes'''

        for attr in self.params_dict.keys():
            if attr not in self._base_attributes:
                raise BIValueError('Attribute <%s> is not expected!'% attr)

        spec_type_name = self.params_dict.get('specification_name', None)
        if not spec_type_name:
            raise BIException('Entity type should be specified')

        if type(self.additional_parameters) != dict:
            raise BIValueError('Additional attributes should has dictionary type')

        if spec_type_name not in self.SPECIFICATIONS:

            raise BIValueError('Entity type "%s" is not expected! %s'% (spec_type_name, self.SPECIFICATIONS))

        spec = self.specification()
        spec.validate_entity(self.additional_parameters)


class Resource(BaseEntity):
    '''
    This class incapsulate resources attributes and operations
    '''

    def __init__(self, *args, **kwargs):
        '''Constructor
        '''
        BaseEntity.__init__(self, *args, **kwargs)
        self._base_attributes += ['resource_status', 'external_system', 'location', 'department', 'owner']

    def validate(self):
        '''Validate resources attributes'''
        BaseEntity.validate(self)

        if self.get_resource_status() is NOT_FOUND:
            raise BIValueError('Resource status is not specified')


class Collection(BaseEntity):
    '''
    This class incapsulate collections attributes and operations
    '''

    def __init__(self, *args, **kwargs):
        '''Constructor
        '''
        BaseEntity.__init__(self, *args, **kwargs)

        self._base_attributes += ['resources']

        if self.get_resources():
            pass
        else:
            self.set_resources([])

    def append_resource(self, resource):
        '''append resource to collection'''
        if not isinstance(resource, Resource):
            raise BIValueError('Object of Resource expected, but <%s> occured!'% self.__class__.__name__)

        spec = self.specification()

        for type_name in spec.get_allowed_types():
            if resource.instance_of(type_name):
                break
        else:
            raise BIValueError('Resource with type <%s> is not allowed for collection <%s>'%
                                                (resource.get_specification_name(), self.get_specification_name()))

        resources = self.get_resources()

        res_id = resource.get__id()

        if res_id is NOT_FOUND:
            raise BIValueError('Resource has not _id attribute (not saved in database).')
        elif res_id in resources:
            raise BIException('Similar resources are not allowed in collection! resource "%s"',res_id)

        resources.append(res_id)
        self.set_resources(resources)

    def remove_resource(self, resource):
        '''remove resource from collection'''
        res_id = resource.get__id()
        if res_id is NOT_FOUND:
            raise BIValueError('Resource has not _id attribute (not saved in database).')

        resources = self.get_resources()
        try:
            resources.remove(res_id)
        except ValueError:
            raise BIValueError('Resource with ID "%s" is not exists in this collection.'%res_id)

        self.set_resources(resources)


class Connection(BaseEntity):
    '''
    This class incapsulate connections attributes and operations
    '''

    def __init__(self, *args, **kwargs):
        '''Constructor
        '''
        BaseEntity.__init__(self, *args, **kwargs)

        self._base_attributes += ['connecting_resource', 'connected_resource']

    def __get_res_id(self, res_type, res_obj, res_desc):
        '''
        Validate resource object and return it ID
        '''
        if not isinstance(res_obj, Resource):
            raise BIValueError('%s resource should has Resource type!'% res_desc)

        if not res_obj.instance_of(res_type):
            raise BIValueError('%s resource should be specified by <%s> specification!'% (res_desc, res_type))

        res_id = res_obj.get__id()
        if res_id is NOT_FOUND:
            raise BIValueError('%s resource has not _id attribute (not saved in database).'% res_desc)

        return res_id

    def connect(self, connecting_res, connected_res):
        '''
        Connect resources if connection specification allowed
        '''
        spec = self.specification()
        connecting_type, connected_type = spec.get_connectors_types()

        connecting_id = self.__get_res_id(connecting_type, connecting_res, 'Connecting')
        connected_id = self.__get_res_id(connected_type, connected_res, 'Connected')

        self.set_connecting_resource(connecting_id)
        self.set_connected_resource(connected_id)