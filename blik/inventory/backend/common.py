
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
        res = {'specification_name': 'Access','resource_status': 'New', 'description': 'Test Acces device', 'external_system': 'test external system', 'location': 'test location',
            'department': 'test department', 'owner': 'test owner',
            'additional_parameters': {'additional_parameters': {'add_param': 'add_value',
                                                                'add_param_2': 'add_value_2'}}}

        return res

    def get_entity_conn(self, ent_type, entity_id):
        res = {'conn_type': 'L2VPN', 'connecting_res_id': 10, 'connected_res_id': 100, 'additional_parameters': {}}

        return res

    def find_entities(self, ent_type, obj_filter):
        pass

    def save_entity(self, ent_type, entity_dict):
        pass

    def remove_entity(self, ent_type, entity_id):
        pass

