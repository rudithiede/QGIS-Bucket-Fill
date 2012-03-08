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
parent = QtGui.QWidget()
canvas = QgsMapCanvas(parent)
canvas.resize(QtCore.QSize(400, 400))
# QgisInterface is a stub implementation of the QGIS plugin interface
iface = QgisInterface(canvas)
myGuiContextFlag = False
GEOCRS = 4326  # constant for EPSG:GEOCRS Geographic CRS id
GOOGLECRS = 900913  # constant for EPSG:GOOGLECRS Google Mercator id


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

    # Add MCL's to the canvas
    # NOTE: New layers *must* be added to the end of this list, otherwise
    #       tests will break.
    canvas.setLayerSet(myCanvasLayers)


def setCanvasCrs(theEpsgId, theOtfpFlag=False):
    """Helper to set the crs for the canvas before a test is run.

    Args:

        * theEpsgId  - Valid EPSG identifier (int)
        * theOtfpFlag - whether on the fly projections should be enabled
                        on the canvas. Default to False.
    """
        # Enable on-the-fly reprojection
    canvas.mapRenderer().setProjectionsEnabled(theOtfpFlag)

    # Create CRS Instance
    myCrs = QgsCoordinateReferenceSystem()
    myCrs.createFromEpsg(theEpsgId)  # google mercator

    # Reproject all layers to WGS84 geographic CRS
    canvas.mapRenderer().setDestinationCrs(myCrs)


class BucketFillTest(unittest.TestCase):
    """
    BucketFill Test Suite.
    """
    def setUp(self):
        self.bucketFill = BucketFill(iface)
        self.bucketFill.initActions()

    def tearDown(self):
        pass

    def prepareTestCanvas(self):
        """
        Sets parameters for a test canvas.
        """
        loadLayers()
        setCanvasCrs(4326, True)
        canvas.resize(QtCore.QSize(400, 400))
        canvas.zoomToFullExtent()

    def testCanvasIsValid(self):
        """
        Check if the plugin has a valid canvas.
        """
        myMessage = "Plugin was not initialised with a valid canvas."
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
        Test that clicking the canvas sets the current class
        color if the layer is a vector layer.
        """
        self.prepareTestCanvas()
        self.bucketFill.setColorForClass(
                                QPoint(200, 200), QtCore.Qt.LeftButton)
        myColor = QColor(canvas.canvasPixmap().toImage().pixel(200, 20))
        # Just for if you want to see what it has rendered
        canvas.saveAsImage('test.png')
        # expected R: 0 G: 48 B: 57
        myExpectedColor = QColor(0, 48, 57)
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
        canvas.zoomToFullExtent()
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
        myPoint = QgsPoint(200, 200)
        myBox = self.bucketFill.getClickBbox(myPoint)
        myExpectedBox = QgsRectangle(199, 199, 201, 201)
        myMessage = ('Bounding box was incorrect. Received values %s'
                     ' Expected values %s' % (str(myBox), str(myExpectedBox)))
        assert myBox == myExpectedBox, myMessage

    def testPixelToCrsBox(self):
        """
        Tests that a bbox in pixel coords is converted to map coords
        """
        self.prepareTestCanvas()
        myMessage = "Plugin was not initialised with a valid canvas."
        assert self.bucketFill.iface.mapCanvas().width() == 400 and \
            self.bucketFill.iface.mapCanvas().height() == 400, myMessage
        myPoint = QgsPoint(200, 200)
        myBox = self.bucketFill.getClickBbox(myPoint)
        self.bucketFill.makeRubberBand(myBox, canvas)
        canvas.setCanvasColor(QColor(255, 255, 255, 255))

        canvas.saveAsImage('/tmp/canvas.png')
        myLayer = self.bucketFill.getActiveVectorLayer()
        myRectangle = self.bucketFill.pixelToCrsBox(myBox, canvas, myLayer)
        myExpectedBox = QgsRectangle(106.758705784, -6.13591899755,
                                     106.761696484, -6.1329282975)
        myMessage = ('Bounding box was incorrect.\n'
            'Received values %s\n'
            'Expected values %s' % (
            str('%s, %s, %s, %s' % (
                myRectangle.xMinimum(), myRectangle.yMinimum(),
                myRectangle.xMaximum(), myRectangle.yMaximum()
                )),
            str('%s, %s, %s, %s' % (
                myExpectedBox.xMinimum(), myExpectedBox.yMinimum(),
                myExpectedBox.xMaximum(), myExpectedBox.yMaximum()
                )),
            ))
        assert (
            round(myRectangle.xMinimum(), 9) ==
            round(myExpectedBox.xMinimum(), 9) and
            round(myRectangle.xMaximum(), 9) ==
            round(myExpectedBox.xMaximum(), 9) and
            round(myRectangle.yMinimum(), 9) ==
            round(myExpectedBox.yMinimum(), 9) and
            round(myRectangle.yMaximum(), 9) ==
            round(myExpectedBox.yMaximum(), 9)), myMessage

    def testGetFirstFeature(self):
        """
        Tests that a feature is returned.
        """
        self.prepareTestCanvas()
        myLayer = self.bucketFill.getActiveVectorLayer()
        myTestBox = QgsRectangle(106.758705784, -6.13591899755,
                                 106.761696484, -6.1329282975)
        myFeature = self.bucketFill.getFirstFeature(myLayer, myTestBox)
        print myFeature
        myMessage = ('Returned object was not a feature.')
        assert myFeature.type() == QgsFeature, myMessage

'''
    def testGetStyleForFeature(self):
        """
        Tests that a style is returned.
        """
        myMessage = ('Force error for unfinished test.')
        assert 1 == 0, myMessage
'''


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
