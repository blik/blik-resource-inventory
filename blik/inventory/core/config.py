#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Purpose: Configure Blik Inventory
Created: 13.09.2012
Author:  Konstantin Andrusenko & Aleksey Bogoslovskyi
"""

import yaml
import sys
sys.path.append('../../../')
from inv_exceptions import BIException
from blik.inventory.backend.mongo import *

#configuration parameters names
CP_BACKEND = 'backend'
CP_DB_CONNSTRING = 'db_connect_string'
CP_DB_NAME = 'db_name'

class InventoryConfiguration:
    def __init__(self, **kw_args):
        self.backend = kw_args.get(CP_BACKEND, None)
        self.db_connect_string = kw_args.get(CP_DB_CONNSTRING, None)
        self.db_name = kw_args.get(CP_DB_NAME, None)

    def _get_config_param(self, config_obj, param_name):
        value = config_obj.get(param_name, None)
        if value is None:
            raise BIException('Configuration parameter <%s> is not found!'% param_name)
        return value

    def from_dict(self, config_obj):
        self.backend = self._get_config_param(config_obj, CP_BACKEND)
        self.db_connect_string = self._get_config_param(config_obj, CP_DB_CONNSTRING)
        self.db_name = self._get_config_param(config_obj, CP_DB_NAME)

    def get_backend_db(self, config_file):
        try:
            conf_obj = yaml.load(open(config_file))
            self.from_dict(conf_obj)
            if self.backend == "mongodb":
                backend_conn_obj = MongoDatabaseAPI(self.db_connect_string, self.db_name)
            else:
                raise BIException("Blik Resource Inventory don't support <%s> backend type!" %self.backend)
            return backend_conn_obj
        except IOError, err:
            raise Exception("Configuration file <%s> is invalid: %s" %(config_file, err.strerror))
        except yaml.YAMLError, exc:
            raise Exception("Error in configuration file <%s>: %s" %(config_file, exc))