from blik.inventory.backend.manager import BackendManager
from blik.inventory.backend.common import  CommonDatabaseAPI
from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
from blik.inventory.core.inv_exception import BIException

class CollectionOperationalAPI():
    def __init__ (self, db_conn):
        self.db_conn = BackendManager.get_scoped_backend()
        self.__cache_entities_types()   

    def createCollection(self, coll_type, **add_params):
        '''Create collection and save it into DB
        @return created collection object'''

        collection = Collection(collection_type=coll_type, additional_parameters=add_params)
        collection.validate()

        coll_id = self.db_conn.save_entity(CommonDatabaseAPI.ET_COLLECTION, collection.to_dict())
        collection.set__id(coll_id)

        return collection

    def deleteCollection(self, coll_id):
        '''Delete collection by ID'''

        self.db_conn.remove_entity(CommonDatabaseAPI.ET_COLLECTION, coll_id)

    def updateCollectionInfo(self, coll_id, **add_params):
        '''Update additional_parameters in collection'''

        collection = self.db_conn.get_entity(CommonDatabaseAPI.ET_COLLECTION, coll_id)

        for param_name, param_value in collection.items():
            collection.set_atrribute(param_name, param_value)

        self.db_conn.save_entity(CommonDatabaseAPI.ET_COLLECTION, collection.to_dict())

        return collection

    def appendResourceToCollection(self, coll_id, res_id):
        '''Add resource to collection'''

        collection = self.db_conn.get_entity(CommonDatabaseAPI.ET_COLLECTION, coll_id)

        if not ResourceOperationalAPI.getResourceInfo(res_id):
            raise BIException ('Resource "%s" is not found in database!'%res_id)

        collection.append_resource(res_id)

    def removeResourceFromCollection(self, coll_id, res_id):
        '''Delete resource from collection'''

        collection = self.db_conn(CommonDatabaseAPI.ET_COLLECTION, coll_id)

        if not ResourceOperationalAPI.getResourceInfo(res_id):
            raise BIException ('Resource "%s" is not found in database!'%res_id)

        collection.remove_resource(res_id)