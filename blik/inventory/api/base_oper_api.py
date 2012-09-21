from blik.inventory.backend.manager import BackendManager
from blik.inventory.backend.common import  CommonDatabaseAPI
from blik.inventory.backend.mongo import  MongoDatabaseAPI
from blik.inventory.core.base_entities import *

ET_SPECIFICATION = 'specification'

class BaseOperationalAPI():
    """return specifications by entity type and entity name"""
    def __init__(self, conn_string, database):
        self.conn_string = conn_string
        self.database = database

        self.db_conn = MongoDatabaseAPI(self.conn_string, self.database)       

    def _cache_entities_types(self, ent_type, ent_name=None):
        pass