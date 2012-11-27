from blik.inventory.utils.ri_spec_manager import  InventoryConfiguration
from blik.inventory.backend.common import  CommonDatabaseAPI
from blik.inventory.core.base_entities import ResourceSpecification, \
                    CollectionSpecification, ConnectionSpecification
from blik.inventory.core.inv_exceptions import BIException 

SPEC_CLASSES = {'resource': ResourceSpecification,
                'collection': CollectionSpecification,
                'connection': ConnectionSpecification }
CONFIG_FILE = "/opt/blik/inventory/conf/blik-ri-conf.yaml"

class ManagementAPI:
    def __init__(self):
        self.conf = InventoryConfiguration()
        self.db_conn = self.conf.get_backend_db(CONFIG_FILE)

    def createSpecification(self, spec_name, parent_spec_name, spec_type, description, **parameters):
        '''Create specification of some entity in Inventory and save it into database
        @return created specification object
        '''
        spec_class = SPEC_CLASSES.get(spec_type, None)

        if spec_class is None:
            raise BIException('Specification type <%s> is not supported!'% spec_type)

        if spec_type == 'resource':
            spec = {'type_name': spec_name,
                    'parent_type_name': parent_spec_name,
                    'spec_type': spec_type,
                    'description': description,
                    'params_spec': parameters['params_spec']}
        elif spec_type == 'connection':
            spec = {'type_name': spec_name,
                    'parent_type_name': parent_spec_name,
                    'spec_type': spec_type,
                    'description': description,
                    'connecting_type': parameters['connecting_type'],
                    'connected_type': parameters['connected_type'],
                    'params_spec': parameters['params_spec']}

        else:
            spec = {'type_name': spec_name,
                    'parent_type_name': parent_spec_name,
                    'spec_type': spec_type,
                    'description': description,
                    'allowed_types': parameters['allowed_types'],
                    'params_spec': parameters['params_spec']}

        spec_obj = spec_class(spec)
        spec_obj.validate()

        self.db_conn.connect()
        res_id = self.db_conn.save_entity(CommonDatabaseAPI.ET_SPECIFICATION, spec_obj.to_dict())
        self.db_conn.close()

        return spec_obj

    def updateSpecification(self, spec_id, spec_name, parent_spec_name, spec_type, description, **parameters):
        '''Update specification of some entity in Inventory and save it into database
        @return created specification object
        '''
        spec_class = SPEC_CLASSES.get(spec_type, None)

        if spec_class is None:
            raise BIException('Specification type <%s> is not supported!'% spec_type)

        self.db_conn.connect()
        raw_spec = self.db_conn.get_entity(CommonDatabaseAPI.ET_SPECIFICATION, spec_id)

        raw_spec['params_spec'] = parameters['params_spec']

        if spec_type == 'resource':
            spec = {'_id': spec_id,
                    'type_name': spec_name,
                    'parent_type_name': parent_spec_name,
                    'spec_type': spec_type,
                    'description': description,
                    'params_spec': raw_spec['params_spec']}
        elif spec_type == 'connection':
            spec = {'_id': spec_id,
                    'type_name': spec_name,
                    'parent_type_name': parent_spec_name,
                    'spec_type': spec_type,
                    'description': description,
                    'connecting_type': parameters['connecting_type'],
                    'connected_type': parameters['connected_type'],                    
                    'params_spec': raw_spec['params_spec']}
        else:
            spec = {'_id': spec_id,
                    'type_name': spec_name,
                    'parent_type_name': parent_spec_name,
                    'spec_type': spec_type,
                    'description': description,
                    'allowed_types': parameters['allowed_types'],                   
                    'params_spec': raw_spec['params_spec']}                    

        spec_obj = spec_class(spec)
        spec_obj.validate()

        self.db_conn.save_entity(CommonDatabaseAPI.ET_SPECIFICATION, spec_obj.to_dict())
        self.db_conn.close()

        return spec_obj

    def getSpecification(self, spec_id):
        '''Get specification of some entity in Inventory from database
        @return found specification object
        '''
        self.db_conn.connect()
        raw_spec = self.db_conn.get_entity(CommonDatabaseAPI.ET_SPECIFICATION, spec_id)
        self.db_conn.close()

        spec_class = SPEC_CLASSES.get(raw_spec['spec_type'], None)

        if spec_class is None:
            raise BIException('Specification type <%s> is not supported!'% raw_spec['spec_type'])

        spec_obj = spec_class(raw_spec)
        #spec_obj.validate()

        return spec_obj

    def findSpecification(self, spec_type, spec_filter):
        '''Find specification by filter and return found Specification objects
        Filter should be dictionary where key = resource attribute with
        optional qualificator suffix (__in, __gt, __ge, __lw, __le)
        '''
        spec_class = SPEC_CLASSES.get(spec_type, None)

        if spec_class is None:
            raise BIException('Specification type <%s> is not supported!'% spec_type)

        self.db_conn.connect()
        raw_specs = self.db_conn.find_entities(CommonDatabaseAPI.ET_SPECIFICATION, spec_filter)
        self.db_conn.close()

        ret_list = []
        for res in raw_specs:
            ret_list.append(spec_class(res))

        return ret_list

    def deleteSpecification(self, spec_id):
        '''Delete specification of some entity in Inventory from database
        '''
        self.db_conn.connect()
        self.db_conn.remove_entity(CommonDatabaseAPI.ET_SPECIFICATION, spec_id)
        self.db_conn.close()