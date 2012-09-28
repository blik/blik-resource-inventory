from blik.inventory.backend.manager import BackendManager
from blik.inventory.backend.common import  CommonDatabaseAPI
from blik.inventory.backend.mongo import  MongoDatabaseAPI
from blik.inventory.core.base_entities import *

ET_SPECIFICATION = 'specification'

class BaseOperationalAPI():
    """return specifications by entity type and entity name"""
    def __init__(self):
		pass     

    def _cache_entities_types(self, ent_type, ent_name=None):
        pass