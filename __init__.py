"""
Bucketfill plugin for QGIS

Contact : rudi@linfiniti.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'rudi@linfiniti.com'
__version__ = '0.1.0'
__date__ = '30/01/2011'
__copyright__ = 'Copyright 2012, Linfiniti Consulting CC.'


def name():
    return "Bucket Fill"


def description():
    return "Changes vector data class styles with a bucket fill tool"


def version():
    return "Version 0.1"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "1.0"


def classFactory(iface):
    # load BucketFill class from file BucketFill
    from gui.bucketfill import BucketFill
    return BucketFill(iface)
