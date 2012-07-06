
class CommonDatabaseAPI:
    #entity types
    ET_RESOURCE = 'resource'
    ET_CONNECTION = 'connection'
    ET_COLLECTION = 'collection'
    ET_SPECIFICATION = 'specification'

    def __init__(self, conn_string):
        self.conn_string = conn_string

    def connect(self):
        pass

    def close(self):
        pass

    def get_entity(self, ent_type, entity_id):
        pass

    def find_entities(self, ent_type, obj_filter):
        pass

    def save_entity(self, ent_type, entity_dict):
        pass

    def remove_entity(self, ent_type, entity_id):
        pass

