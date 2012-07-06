
import os

import yaml

from inv_exceptions import BIException


#configuration parameters names
CP_BACKEND = 'backend'
CP_DB_CONNSTRING = 'db_connect_string'

class InventoryConfiguration:
    def __init__(self, **kw_args):
        self.backend = kw_args.get(CP_BACKEND, None)
        self.db_connect_string = kw_args.get(CP_DB_CONNSTRING, None)

    def __get_config_param(self, config_obj, param_name):
        value = config_obj.get(param_name, None)
        if value is None:
            raise BIException('Configuration parameter <%s> is not found!'% param_name)

        return value

    def from_dict(self, config_obj):
        self.backend = self.__get_config_param(config_obj, CP_BACKEND)
        self.db_connect_string = self.__get_config_param(config_obj, CP_DB_CONNSTRING)

    def from_config_file(self, config_file):
        if not os.path.exists(config_file):
            raise BIException('File %s is not found!'% config_file)

        f_obj = open(file_path)

        try:
            conf_obj = yaml.load(f_obj)
        except Exception, err:
            raise BIException('File %s is not found!'%file_path)
        finally:
            f_obj.close()

        self.from_dict(conf_obj)

