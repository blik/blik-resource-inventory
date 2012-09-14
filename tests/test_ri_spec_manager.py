#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import unittest
from pymongo import Connection
from blik.inventory.utils.ri_spec_manager import *

DUMP_FILES_LOCATION = "/tmp/BlikRISpecManager"
DB_NAME = "Test_BlikRI"

def prepare():
    #   Clear test directory
    if os.path.exists(DUMP_FILES_LOCATION):
        shutil.rmtree(DUMP_FILES_LOCATION)
    os.mkdir(DUMP_FILES_LOCATION)
    #   Clear specification coollection in Test DB
    conn = Connection()
    coll = conn[DB_NAME][CommonDatabaseAPI.ET_SPECIFICATION]
    coll.remove()
    conn.disconnect()

class TestSpecificationManager(unittest.TestCase):
    def test_01_check_key(self, object = {"specifications" : [{"type_name": "Interface"}, {"type_name": "Device"}]}, key = "some_key"):
        spec = SpecificationManager()
        self.assertRaises(Exception, spec.check_key, object, key)

    def test_02_restore_spec(self, spec_file = "./tests/simple_spec.yaml", filter = None):
        spec = SpecificationManager()
        #   Try restore specifications from not existing file
        self.assertRaises(Exception, spec.restore_spec, "/wrong/path/to/restore/spec.file")
        #   Try restore specifications from file with wrong syntax
        self.assertRaises(Exception, spec.restore_spec, "./tests/wrong_simple_spec.yaml")
        #   Restore specifications from file
        spec.restore_spec(spec_file)
        part_insert_data = [{'type_name': 'Device', 'parameters': [{'default_value': 1, 'param_name': 'test_param', 'mandatory': False, 'description': 'some descr', 'param_type': 'integer', 'possible_values': [1, 2, 3, 4]}]}]
        conn = Connection()
        result = []
        for item in conn[DB_NAME][CommonDatabaseAPI.ET_SPECIFICATION].find({"type_name": "Device"}):
            item.pop("_id")
            result.append(item)
        self.assertEqual(part_insert_data, result)

    def test_03_dump_spec(self, spec_file = "/wrong/path/to/dump/spec.file", filter = None):
        spec = SpecificationManager()
        #   Try dump specifications to wrong file(wrong path or permissions)
        self.assertRaises(Exception, spec.dump_spec, spec_file)
        #   Dump all types specifications
        spec_file = os.path.join(DUMP_FILES_LOCATION, "full_dump_spec.yaml")
        spec.dump_spec(spec_file)
        self.assertTrue(os.path.isfile(spec_file))
        #   Dump only "Device" type specifications
        spec_file = os.path.join(DUMP_FILES_LOCATION, "device_dump_spec.yaml")
        spec.dump_spec(spec_file, ["Device"])
        self.assertTrue(os.path.isfile(spec_file))

if __name__ == '__main__':
    prepare()
    unittest.main()