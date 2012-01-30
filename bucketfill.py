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
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from bucketfilldialog import BucketFillDialog

class BucketFill:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(":/plugins/bucketfill/icon.png"), \
            "Bucket fill", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Bucket fill", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&Bucket fill",self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        myColorSelect = QColorDialog.getColor()
        #myColorSelect = BucketFillDialog()
        if QColor.isValid(myColorSelect):
            # do something useful
            pass
