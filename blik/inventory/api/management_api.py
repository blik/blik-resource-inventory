from blik.inventory.backend.manager import BackendManager
from blik.inventory.backend.common import  CommonDatabaseAPI
from blik.inventory.core.base_entities import ResourceSpecification,
                    CollectionSpecification, ConnectionSpecification

SPEC_CLASSES = {'resource': ResourceSpecification,
                'collection': CollectionSpecification,
                'connection': ConnectionSpecification }

class ManagementAPI:
    def __init__(self, db_conn):
        self.db_conn = BackendManager.get_scoped_backend()

    def createSpecification(self, spec_name, parent_spec_name, spec_type, **parameters):
        '''Create specification of some entity in Inventory and save it into database
        @return created specification object
        '''
        spec_class = SPEC_CLASSES.get(spec_type, None)

        spec = {'type_name': spec_name,
                'parent_type_name': parent_spec_name,
                'spec_type': spec_type,
                'params_spec': parameters}

        if spec_class is None:
            raise RIException('Specification type <%s> is not supported!'% spec_type)

        spec_obj = spec_class(spec)
        spec_obj.validate()

        res_id = self.db_conn.save_entity(CommonDatabaseAPI.ET_SPECIFICATION, spec_obj.to_dict())

        spec_obj.set__id(res_id)

        return spec_obj

    def updateSpecification(self, spec_id, spec_name, parent_spec_name, spec_type, **parameters):
        '''Update specification of some entity in Inventory and save it into database
        @return created specification object
        '''
        spec_class = SPEC_CLASSES.get(spec_type, None)

        if spec_class is None:
            raise RIException('Specification type <%s> is not supported!'% spec_type)

        raw_spec = self.db_conn.get_entity(CommonDatabaseAPI.ET_SPECIFICATION, spec_id)

        spec = {'__id': spec_id,
                'type_name': spec_name,
                'parent_type_name': parent_spec_name,
                'spec_type': spec_type,
                'params_spec': raw_spec['params_spec'].update(parameters)}

        spec_obj = spec_class(spec)
        spec_obj.validate()

        res_id = self.db_conn.save_entity(CommonDatabaseAPI.ET_SPECIFICATION, spec_obj.to_dict())

        return spec_obj

    def getSpecification(self, spec_id):
        '''Get specification of some entity in Inventory from database
        @return found specification object
        '''
        raw_spec = self.db_conn.get_entity(CommonDatabaseAPI.ET_SPECIFICATION, spec_id)

        spec_class = SPEC_CLASSES.get(raw_spec['spec_type'], None)

        if spec_class is None:
            raise RIException('Specification type <%s> is not supported!'% spec_type)

        spec_obj = spec_class(raw_spec)
        spec_obj.validate()

        return spec_obj

    def deleteSpecification(self, spec_id):
        '''Delete specification of some entity in Inventory from database
        '''
        self.db_conn.delete_entity(CommonDatabaseAPI.ET_SPECIFICATION, spec_id)