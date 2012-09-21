
class CommonDatabaseAPI:
    #entity types
    ET_RESOURCE = 'resource'
    ET_CONNECTION = 'connection'
    ET_COLLECTION = 'collection'
    ET_SPECIFICATION = 'specification'
    SUPPORTED_ENT_TYPES = [ET_RESOURCE, ET_CONNECTION, ET_COLLECTION, ET_SPECIFICATION]
    
    def __init__(self, conn_string):
        self.conn_string = conn_string

    def connect(self):
        pass

    def close(self):
        pass

    def get_entity(self, ent_type, entity_id):
        pass

    def get_entity_conn(self, ent_type, entity_id):
        pass

    def find_entities(self, ent_type, obj_filter):
        pass

    def save_entity(self, ent_type, entity_dict):
        pass

    def remove_entity(self, ent_type, entity_id):
        pass

