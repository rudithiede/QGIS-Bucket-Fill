"""
/***************************************************************************
 BucketFillDialog
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

from PyQt4 import QtCore, QtGui
from ui_bucketfill import Ui_BucketFill
# create the dialog for zoom to point
class BucketFillDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_BucketFill()
        self.ui.setupUi(self)
