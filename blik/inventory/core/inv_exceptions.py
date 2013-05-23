#!/usr/bin/python
#pylint: disable=C0301
"""
Purpose: Blik Inventory exceptions
Created: 29.01.2012
Author:  Konstantin Andrusenko
"""

class BIException(Exception):
    def __str__(self):
        return '[Blik Inventory Exception] %s'% \
                Exception.__str__(self)

class BIValueError(BIException):
    def __str__(self):
        return '[Blik Inventory ValueError] %s'% \
                Exception.__str__(self)
