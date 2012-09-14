#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from blik.inventory.core.config import InventoryConfiguration
from blik.inventory.core.inv_exceptions import *

CONF_OBJ_DICT = {"backend":"mongodb", "db_connect_string": "localhost:27017", "db_name": "Test_BlikRI"}

class TestInventoryConfiguration(unittest.TestCase):
    def test_01__get_config_param(self, config_obj = CONF_OBJ_DICT, param_name = "backend"):
        #   Try get not existing configuration parameter
        conf = InventoryConfiguration()
        self.assertRaises(BIException, conf._get_config_param, CONF_OBJ_DICT, "fake_param_name")

        #   Get configuration parameter
        result = conf._get_config_param(CONF_OBJ_DICT, "backend")
        self.assertEqual(result, "mongodb")

    def test_02_get_backend_db(self, config_file = "/blik-ri-conf.yaml"):
        conf = InventoryConfiguration()
        #   Use wrong path to configuration file
        self.assertRaises(Exception, conf.get_backend_db, "/some/fake/path/to.file")
        #   Use wrong configuration file syntax
        self.assertRaises(Exception, conf.get_backend_db, "./tests/wrong-blik-ri-conf.yaml")
        #   Use wrong backend configuration parameter
        self.assertRaises(Exception, conf.get_backend_db, "./tests/wrong-blik-ri-conf_2.yaml")
        #   Use wrong path to configuration file
        conn_obj = conf.get_backend_db("./blik/inventory/conf/blik-ri-conf.yaml")
        self.assertEqual(isinstance(conn_obj, object), True)

if __name__ == '__main__':
    unittest.main()