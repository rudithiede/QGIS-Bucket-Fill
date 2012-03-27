"""Testing the bucketfill plugin.

Contact : tim@linfiniti.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.1.0'
__date__ = '30/01/2011'
__copyright__ = 'Copyright 2012, Linfiniti Consulting CC.'

import os
import unittest
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QPoint
from PyQt4.QtGui import QColor
#from PyQt4.QtTest import QTest
from qgis.core import (QgsProviderRegistry,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsMapLayerRegistry,
                       QgsCoordinateReferenceSystem,
                       QgsPoint,
                       QgsRectangle,
                       QgsFeature)
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer
from qgisinterface import QgisInterface
from utilities_test import globalQgis
from bucketfill import BucketFill

# Get QGis app handle
QGISAPP = globalQgis()
# Set form to test against
PARENT = QtGui.QWidget()
CANVAS = QgsMapCanvas(PARENT)
CANVAS.resize(QtCore.QSize(400, 400))
CANVAS.refresh()
# QgisInterface is a stub implementation of the QGIS plugin interface
IFACE = QgisInterface(CANVAS)
GUI_CONTEXT_FLAG = False
GEOCRS = 4326  # constant for EPSG:GEOCRS Geographic CRS id
GOOGLECRS = 900913  # constant for EPSG:GOOGLECRS Google Mercator id

TEST_BOX = (106.773659284, -6.13591899755, 106.776649984, -6.1329282975)


def loadLayers():
    """
    Helper function to load layers into the dialog.
    """

    # First unload any layers that may already be loaded
    for myLayer in QgsMapLayerRegistry.instance().mapLayers():
        QgsMapLayerRegistry.instance().removeMapLayer(myLayer)

    # Now go ahead and load our layers

    myRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    myData = os.path.join(myRoot, 'test_data')
    myData = myData.replace('Tim Sutton', 'TIMSUT~1')
    myData = myData.replace('Rudi Thiede', 'RUDI~1')

    # List all layers in the correct order.
    myFileList = ['test.shp']

    myCanvasLayers = []
    for myFile in myFileList:
        # Extract basename and absolute path
        myBaseName, myExt = os.path.splitext(myFile)
        myPath = os.path.join(myData, myFile)

        # Create QGis Layer Instance
        if myExt in ['.asc', '.tif']:
            myLayer = QgsRasterLayer(myPath, myBaseName)
        elif myExt in ['.shp']:
            myLayer = QgsVectorLayer(myPath, myBaseName, 'ogr')
        else:
            msg = 'File %s had illegal extension' % myPath
            raise Exception(msg)

        msg = 'Layer "%s" is not valid' % str(myLayer.source())
        assert myLayer.isValid(), msg

        # Add layer to the registry (that QGis knows about)
        QgsMapLayerRegistry.instance().addMapLayer(myLayer)

        # Create Map Canvas Layer Instance and add to list
        myCanvasLayers.append(QgsMapCanvasLayer(myLayer))

    # Add MCL's to the CANVAS
    # NOTE: New layers *must* be added to the end of this list, otherwise
    #       tests will break.
    CANVAS.setLayerSet(myCanvasLayers)


def setCanvasCrs(theEpsgId, theOtfpFlag=False):
    """Helper to set the crs for the CANVAS before a test is run.

    Args:

        * theEpsgId  - Valid EPSG identifier (int)
        * theOtfpFlag - whether on the fly projections should be enabled
                        on the CANVAS. Default to False.
    """
        # Enable on-the-fly reprojection
    CANVAS.mapRenderer().setProjectionsEnabled(theOtfpFlag)

    # Create CRS Instance
    myCrs = QgsCoordinateReferenceSystem()
    myCrs.createFromEpsg(theEpsgId)  # google mercator

    # Reproject all layers to WGS84 geographic CRS
    CANVAS.mapRenderer().setDestinationCrs(myCrs)


class BucketFillTest(unittest.TestCase):
    """
    BucketFill Test Suite.
    """
    def setUp(self):
        self.bucketFill = BucketFill(IFACE)
        self.bucketFill.initActions()

    def tearDown(self):
        pass

    def prepareTestCanvas(self):
        """
        Sets parameters for a test CANVAS.
        """
        loadLayers()
        setCanvasCrs(4326, True)
        CANVAS.resize(QtCore.QSize(400, 400))
        CANVAS.zoomToFullExtent()

    def testCanvasIsValid(self):
        """
        Check if the plugin has a valid CANVAS.
        """
        myMessage = "Plugin was not initialised with a valid CANVAS."
        assert self.bucketFill.iface.mapCanvas().width() == 400, myMessage

    def testEnableBucketTool(self):
        """
        Check that enabling the bucket tool works.
        """
        self.bucketFill.enableBucketTool()
        myMessage = 'Unable to enable the bucketfill map tool'
        assert self.bucketFill.bucketFillAction.isEnabled(), myMessage

    def testSetColorForClass(self):
        """
        Test that clicking the CANVAS sets the current class
        color if the layer is a vector layer.
        """
        self.prepareTestCanvas()
        #self.bucketFill.setColorForClass(
        #                        QPoint(50, 15), QtCore.Qt.LeftButton)
        myColor = QColor(CANVAS.canvasPixmap().toImage().pixel(50, 15))
        # Just for if you want to see what it has rendered
        CANVAS.saveAsImage('test.png')
        # expected R: 182 G: 109 B: 194
        myExpectedColor = QColor(182, 109, 194)
        myMessage = (('Unexpected color\n Received R: %i G: %i B: %i '
                    '\n Expected: R: %i G: %i B: %i') %
                      (myColor.red(),
                       myColor.green(),
                       myColor.blue(),
                       myExpectedColor.red(),
                       myExpectedColor.green(),
                       myExpectedColor.blue()))
        assert myColor == myExpectedColor, myMessage

    def testQGISEnvironment(self):
        """
        QGIS environment has the expected providers.
        """

        r = QgsProviderRegistry.instance()
        #for item in r.providerList():
        #    print str(item)

        print 'Provider count: %s' % len(r.providerList())
        assert 'gdal' in r.providerList()
        assert 'ogr' in r.providerList()

    def testGetActiveVectorLayer(self):
        """
        Tests that the active layer is a vector.
        """
        #check when no layers are loaded that an exception is thrown
        myExceptionFlag = False
        myLayer = None
        try:
            myLayer = self.bucketFill.getActiveVectorLayer()
        except:
            #good we expect an error!
            myExceptionFlag = True
        myMessage = ('Expected an exception to be raised when no layer'
                     'is present, but none was received.')
        assert myExceptionFlag == True, myMessage

        # Now test that when a layer is loaded that we get
        # the expected response
        loadLayers()
        CANVAS.zoomToFullExtent()
        try:
            myLayer = self.bucketFill.getActiveVectorLayer()
        except:
            myErrorMessage = 'Layer could not be identified as a vector.'
            assert myLayer.isValid(), myErrorMessage

    def testGetStyleClassList(self):
        """
        Tests that a list of classes is received.
        """
        loadLayers()
        myLayer = self.bucketFill.getActiveVectorLayer()
        myList = self.bucketFill.getStyleClassList(myLayer)
        myMessage = 'Style list for layer is empty.'
        assert len(myList) > 0, myMessage

    def testGetClickBbox(self):
        """
        Tests that a click returns a small bbox.
        """
        # pixel coords for fake click
        self.prepareTestCanvas()
        myPoint = QgsPoint(50, 15)
        myBox = self.bucketFill.getClickBbox(myPoint)
        myExpectedBox = QgsRectangle(49.99850465,
                                     14.99850465,
                                     50.00149535,
                                     15.00149535)
        myMessage = ('Bounding box was incorrect. Received values %s'
                     ' Expected values %s' % (
                        str('%s, %s, %s, %s' % (
                            myBox.xMinimum(), myBox.yMinimum(),
                            myBox.xMaximum(), myBox.yMaximum()
                            )),
                        str('%s, %s, %s, %s' % (
                            myExpectedBox.xMinimum(), myExpectedBox.yMinimum(),
                            myExpectedBox.xMaximum(), myExpectedBox.yMaximum()
                            ))
                    ))
        assert (round(myBox.xMinimum(), 9) ==
                round(myExpectedBox.xMinimum(), 9) and
                round(myBox.xMaximum(), 9) ==
                round(myExpectedBox.xMaximum(), 9) and
                round(myBox.yMinimum(), 9) ==
                round(myExpectedBox.yMinimum(), 9) and
                round(myBox.yMaximum(), 9) ==
                round(myExpectedBox.yMaximum(), 9)), myMessage

    def testGetFirstFeature(self):
        """
        Tests that a feature is returned.
        """
        self.prepareTestCanvas()
        myLayer = self.bucketFill.getActiveVectorLayer()
        myTestBox = QgsRectangle(TEST_BOX[0], TEST_BOX[1],
                                 TEST_BOX[2], TEST_BOX[3])

        myFeature = self.bucketFill.getFirstFeature(myLayer, myTestBox)
        print myFeature
        myMessage = ('Returned object was not a feature.')
        assert myFeature.type() == QgsFeature, myMessage

"""
    def testGetStyleForFeature(self):
        '''
        Tests that a style is returned.
        '''
        myMessage = ('Force error for unfinished test.')
        assert 1 == 0, myMessage
"""


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
