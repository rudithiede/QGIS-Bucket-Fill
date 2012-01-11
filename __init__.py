"""
/***************************************************************************
 BucketFill
                                 A QGIS plugin
 Changes vector data class styles with a bucket fill tool
                             -------------------
        begin                : 2012-01-11
        copyright            : (C) 2012 by Linfiniti CC
        email                : rudi@linfiniti.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
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
    from bucketfill import BucketFill
    return BucketFill(iface)
