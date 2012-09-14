#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Purpose: Utility for easy dump/restore specifications in/from YAML-file
Created: 01.09.2012
Author:  Aleksey Bogoslovskyi
"""

import sys
import yaml
import optparse
sys.path.append('../../../')
from blik.inventory.core.config import *

CONFIG_FILE = "../../../conf/blik-ri-conf.yaml"

class SpecificationManager:
    def __init__(self):
        self.collection = CommonDatabaseAPI.ET_SPECIFICATION
        
    def spec_manager(self):
        usage = "%prog [OPTION] [VALUE] ... [OPTION] [VALUE]"
        p = optparse.OptionParser(usage=usage)
        p.add_option("-d", "--dump", action="store", dest="dump_file", help = "Get specification from DataBase and save into file")
        p.add_option("-r", "--restore", action="store", dest="restore_file", help = "Put specification into DataBase from incoming file")
        p.add_option("-s", "--specify", action="store", dest="filter", help = "Determine type of specification for processing. Optional parameter")
        opts, args = p.parse_args()
        
        if len(sys.argv) < 2 or args:
            p.error("Please, input correct number of arguments. Use -h or --help option to call help")
        if opts.dump_file and opts.restore_file:
            p.error("Error. You must use \"dump\" and \"restore\" options separately")
            
        if opts.filter:
            filter = [item.strip() for item in opts.filter.split(",")]
        else:
            filter = []
            
        if opts.dump_file:
            self.dump_spec(opts.dump_file, filter)
        elif opts.restore_file:
            self.restore_spec(opts.restore_file, filter)

    ##### Restore Specification (Put specifications into DB)#####
    def check_key(self, object, key):
        if object.get(key, None) is None:
            raise Exception("Parameter \"%s\" is not specified in file"%key)

    def restore_spec(self, spec_file, filter = None):
        try:
            yaml_config = yaml.load(open(spec_file))
        except IOError, err:
            raise Exception("Configuration file is invalid:", err)
        except yaml.YAMLError, exc:
            raise Exception("Error in configuration file:", exc)
        self.check_key(yaml_config, "specifications")
        conf = InventoryConfiguration()
        connection = conf.get_backend_db(CONFIG_FILE)
        connection.connect()
        for params in yaml_config["specifications"]:
            self.check_key(params, "type_name")
            if filter:
                if not ((params["type_name"] in filter) or (params.has_key("parent_type_name") and params["parent_type_name"] in filter)):
                    continue
            connection.save_entity(self.collection, params)
        connection.close()

    ##### Dump Specification (Get specifications from DB)#####
    def unicode_representer(self, dumper, uni):
        node = yaml.ScalarNode(tag=u'tag:yaml.org,2002:str', value=uni)
        return node

    def dump_spec(self, spec_file, filter = None):
        yaml.add_representer(unicode, self.unicode_representer)
        conf = InventoryConfiguration()
        connection = conf.get_backend_db(CONFIG_FILE)
        connection.connect()
        if filter:
            query = {"type_name__in": filter}
        else:
            query = {}
        list = []
        for item in connection.find_entities(self.collection, query):
            list.append(item)

        try:
            spec = open(spec_file, 'w')
            yaml.dump({"specifications" : list}, spec)
            spec.close()
        except:
            raise Exception("Can't create spec-file %s. Please, check permissions and path to file." %(spec_file))
        finally:
            connection.close()

if __name__ == '__main__':
    spec = SpecificationManager()
    spec.spec_manager()
