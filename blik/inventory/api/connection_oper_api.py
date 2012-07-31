from blik.inventory.backend.manager import BackendManager
from blik.inventory.backend.common import  CommonDatabaseAPI
from blik.inventory.api.resource_oper_api import ResourceOperationalAPI
from blik.inventory.core.inv_exceptions import BIException
from blik.inventory.core.base_entities import *

BOTH = ['connecting_res_id', 'connected_res_id']
CONNECTING = 'connecting_res_id'
CONNECTED = 'connected_res_id'

class ConnectionOperationalAPI():
    def __init__(self, db_conn):
        self.db_conn = CommonDatabaseAPI(db_conn)#BackendManager.get_scoped_backend()
        #self.__cache_entities_types()

    def updateConnection(self, conn_id, conn_type=None, connecting_res_id=None, connected_res_id=None, **add_params ):
        '''Update connection information.
        Find connection in database by ID and update all non-None passed attributes.
        '''

        raw_connection = self.db_conn.get_entity_conn(CommonDatabaseAPI.ET_CONNECTION, conn_id)

        connection = Connection(raw_connection)
        print connection.to_dict()

        if conn_type != None:
            connection.set_connection_type(conn_type)
        if connecting_res_id != None:
            connection.set_connecting_res_id(connecting_res_id)
        if connected_res_id != None:
            connection.set_connected_res_id(connected_res_id)

        for param_name, param_value in add_params.items():
            connection.set_attribute(param_name, param_value)

        connection.connect(connecting_res_id, connected_res_id)
        self.db_conn.save_entity(CommonDatabaseAPI.ET_CONNECTION, connection.to_dict())

        return connection

    def findConnection(self, **connection_filter):
        '''Find connection by filter and return found Connection objects.
        Filter should be dictionary where key = resource attribute with
        optional qualificator suffix (__in, __gt, __ge, __lw, __le, __all).
        '''

        raw_connection = self.db_conn.find_entities(CommonDatabaseAPI.ET_CONNECTION, connection_filter)

        ret_list = []
        for res in raw_connection:
            ret_list.append(Connection(res))

        return ret_list

    def connectResources(self, conn_type, connecting_res_id, connected_res_id, **add_params):
        '''Connecting resource by connect type'''
        
        filter_res = {'resource_id__all': [connecting_res_id, connected_res_id]}
        filter_conn = {'connection_type': conn_type,
                       'connecting_res_id': connecting_res_id,
                       'connected_res_id': connected_res_id,
                       'additional_parameters': add_params}

        connection = Connection(connecting_resource=connecting_res_id, connected_resource=connected_res_id)

        spec = ConnectionSpecification(conn_type)

        if not ResourceOperationalAPI.findResources(filter_res):
            raise BIException('One of resource is not found in database!')
        if findConnection(filter_conn):
            raise BIException('Connection between resources "%s" and "%s" by type "%s" already exist!'%(connecting_res_id, connected_res_id, conn_type))
        #if connection.validate(): #validation spec for connection
        #    connection.connect()
        #    self.db_conn.save_entity(CommonDatabaseAPI.ET_CONNECTION, connection.to_dict())
        else:
            raise BIException ('Connection is not allowed for resources "%s" and "%s"!'%
                                (connecting_res_id, connected_res_id))

    def disconnectResourcesById(self, connection_id):
        '''Disconnect resource by connection ID '''

        self.db_conn.remove_entity(CommonDatabaseAPI.ET_CONNECTION, connection_id)

    def disconnectResources(self, conn_type, connecting_res_id, connected_res_id):
        '''Disconnect resource'''

        filter_conn = {'connection_type': conn_type,
                       'connecting_res_id': connecting_res_id,
                       'connected_res_id': connected_res_id}

        if findConnection(filter_conn):
            self.db_conn.remove_entity(CommonDatabaseAPI.ET_CONNECTION, filter_conn)
        else:
            raise BIException ('Connection is not found in database!')

    def getLinkedResources(self, resource_id, conn_type=None, conn_direction=BOTH):
        '''Get linked resource by direction'''

        filter_both = {}
        for key in BOTH:
            filter_both.update({'connection_type': conn_type, key: resource_id, })

        filter_conn = {'connection_type': conn_type, CONNECTING: resource_id}
        filter_conned = {'connection_type': conn_type, CONNECTED: resource_id}

        if conn_direction == BOTH:
            return findConnection(filter_both)
        elif conn_direction == CONNECTING:
            return findConnection(filter_conn)
        elif conn_direction == CONNECTED:
            return findConnection(filter_conned)
        else:
            raise BIException ('Connection directions "%s" is not correct!'%conn_direction)    