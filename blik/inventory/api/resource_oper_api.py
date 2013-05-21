from blik.inventory.backend.common import  CommonDatabaseAPI
from blik.inventory.utils.ri_spec_manager import  InventoryConfiguration
from blik.inventory.core.base_entities import Resource

CONFIG_FILE = "/opt/blik/inventory/conf/blik-ri-conf.yaml"

class ResourceOperationalAPI:
    def __init__(self):
        self.conf = InventoryConfiguration()
        self.db_conn = self.conf.get_backend_db(CONFIG_FILE)

    def createResource(self, resource_type, status, description=None,
                    external_system=None, location=None, department=None, owner=None, **add_params):
        '''Create resource object and save it into database
        @return created resource object
        '''

        resource = Resource(specification_name=resource_type, resource_status=status,
                description=description, external_system=external_system, location=location,
                department=department, owner=owner, additional_parameters=add_params.itervalues().next())
        resource.validate()

        self.db_conn.connect()
        res_id = self.db_conn.save_entity(CommonDatabaseAPI.ET_RESOURCE, resource.to_dict())
        self.db_conn.close()

        resource.set__id(res_id)

        return resource

    def updateResource(self, resource_id, status=None, description=None, external_system=None,
                    location=None, department=None, owner=None, **add_params):
        '''Update resource information
        Find resource in database by ID and update all non-None passed attributes
        '''

        self.db_conn.connect()
        raw_resource = self.db_conn.get_entity(CommonDatabaseAPI.ET_RESOURCE, resource_id)
        resource = Resource(raw_resource)

        if status != None:
            resource.set_resource_status(status)
        if description != None:
            resource.set_description(description)
        if external_system != None:
            resource.set_external_system(external_system)
        if location != None:
            resource.set_location(location)
        if department != None:
            resource.set_department(department)
        if owner != None:
            resource.set_owner(owner)

        for param_name, param_value in add_params.items():
            for key, value  in param_value.items():
                resource.set_attribute(key, value)

        resource.validate()
        self.db_conn.save_entity(CommonDatabaseAPI.ET_RESOURCE, resource.to_dict())
        self.db_conn.close()

        return resource

    def getResourceInfo(self, resource_id):
        '''Find resource in database by ID and return Resource object
        '''

        self.db_conn.connect()
        raw_resource = self.db_conn.get_entity(CommonDatabaseAPI.ET_RESOURCE, resource_id)
        self.db_conn.close()

        resource = Resource(raw_resource)

        return resource

    def findResources(self, resource_filter):
        '''Find resources by filter and return found Resource objects
        Filter should be dictionary where key = resource attribute with
        optional qualificator suffix (__in, __gt, __ge, __lw, __le)
        '''
        #print resource_filter
        self.db_conn.connect()
        raw_resources = self.db_conn.find_entities(CommonDatabaseAPI.ET_RESOURCE, resource_filter)
        self.db_conn.close()
        #print raw_resources
        ret_list = []
        for res in raw_resources:
            ret_list.append(Resource(res))

        return ret_list

    def removeResource(self, resource_id):
        '''Remove resource from database'''

        self.db_conn.connect()
        self.db_conn.remove_entity(CommonDatabaseAPI.ET_RESOURCE, resource_id)
        self.db_conn.close()