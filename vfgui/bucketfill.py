"""
Bucketfill Implementation

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

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import QObject, SIGNAL
from PyQt4.QtGui import QAction, QIcon, QColorDialog, QColor
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsRectangle
from qgis.core import QgsMapLayer
from qgis.core import QgsCoordinateTransform
# Initialize Qt resources from file resources.py
import resources


class BucketFill:
    """A little plugin to allow you to set the colour of a vector
    class by clicking on it."""
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.bucketTool = QgsMapToolEmitPoint(self.iface.mapCanvas())

    def initGui(self):
        """Called by QGIS to add gui elements to its Mainwindow
         etc. BucketFill class.

        Args:
            None
        Returns:
            None
        Raises:
            None

        """
        self.initActions()
        # Add toolbar button and menu item - colour chooser
        self.iface.addToolBarIcon(self.colourChooserAction)
        self.iface.addPluginToMenu("&Bucket fill", self.colourChooserAction)
        # Add toolbar button and menu item - map tool
        self.iface.addToolBarIcon(self.bucketFillAction)
        self.iface.addPluginToMenu("&Bucket fill", self.bucketFillAction)

    def initActions(self):
        """Setup actions. Implemented in a separate function so it can
        be used in the context of our testing framework.

        Args:
            None
        Returns:
            None
        Raises:
            None

        """
        # Create action that will start plugin configuration
        self.colourChooserAction = (QAction(
                    QIcon(":/plugins/bucketfill/icon.png"),
                    "Bucket fill", self.iface.mainWindow()))
        self.bucketFillAction = (QAction(
                    QIcon(":/plugins/bucketfill/bucket.png"),
                    "Bucket fill", self.iface.mainWindow()))
        # connect the action to the chooseColour method
        QObject.connect(self.colourChooserAction,
                    SIGNAL("triggered()"), self.chooseColour)
        QObject.connect(self.bucketFillAction,
                    SIGNAL("triggered()"), self.enableBucketTool)
        QObject.connect(self.bucketTool,
                    SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"),
                    self.setColorForClass)

    def unload(self):
        """Constructor for the BucketFill class.

        Args:
            None
        Returns:
            None
        Raises:
            None

        """
        self.iface.removePluginMenu("&Bucket fill", self.action)
        self.iface.removeToolBarIcon(self.action)

    def chooseColour(self):
        """Show a colour picker to let the user choose a colour.

        Args:
            None
        Returns:
            None
        Raises:
            None

        """
        myColorSelect = QColorDialog.getColor()
        #myColorSelect = BucketFillDialog()
        if QColor.isValid(myColorSelect):
            # do something useful
            pass

    def enableBucketTool(self):
        """Make the bucket tool active on the canvas.

        Args:
            None
        Returns:
            None
        Raises:
            None

        """
        self.iface.mapCanvas().setMapTool(self.bucketTool)

    def setColorForClass(self, thePoint, theButton):
        """Set the colour of the active layer's feature
        class that falls under the cursor

        Args:

            * thePoint - a QgsPoint indicating where the click on
                the canvas took place.
            * theButton - a Qt::MouseButton enumerator indicating
                which button was clicked with

        Returns:
            None
        Raises:
            None

        """
        # get the canvas
        myCanvas = self.iface.mapCanvas()

        # get the active layer
        myLayer = self.getActiveVectorLayer()

        # get style class list
        myStyles = self.getStyleClassList(myLayer)

        # identify click xy on canvas (pixel coords)
        myClickBox = self.getClickBbox(thePoint)

        # convert myClickBox to map coords
        myExtent = self.pixelToCrsBox(myClickBox, myCanvas, myLayer)

        # use provider to select based on attr and bbox, and get first feature
        # from resulting list
        myFeature = self.getFirstFeature(myLayer, myExtent)

        # find the symbol for said feature
        mySymbol = self.getSymbolForFeature(myFeature)
        # clone class
        # set fill color for class
        # replace original with altered clone
        # refresh the canvas

    def getActiveVectorLayer(self):
        """Get the active vector layer.

        Args:
            None
        Returns:
            A valid QGIS vector layer
        Raises:
            An exception if current layer is not a vector layer

        """
        # get active layer for canvas
        myLayer = self.iface.activeLayer()
        if myLayer is None:
            myMessage = ('There is no current layer. Load a vector layer and '
                         'select it before using it.')
            raise Exception(myMessage)
        # check that it's a vector
        if myLayer.type() == QgsMapLayer.VectorLayer:
            return myLayer
        else:
            myMessage = 'Current layer is not a vector layer.'
            raise Exception(myMessage)

    def getStyleClassList(self, theLayer):
        """
        Get the list of style classes in the given layer.

        Args:
            Object: the active layer.
        Returns:
            A list of styles from the given layer.
        Raises:
            Exception if symbol type is unknown.
            Exception if layer uses old symbology.
        """
        if not theLayer.isUsingRendererV2():
            myMessage = ('This plugin does not currently'
                         ' support old symbology.')
            raise Exception(myMessage)

        myRenderer = theLayer.rendererV2()
        myType = myRenderer.type()
        myStylesList = []
        if myType == 'singleSymbol':
            mySymbol = myRenderer.symbol()
            myStylesList.append(mySymbol)
        elif myType == 'categorizedSymbol':
            for myCategory in myRenderer.categories():
                mySymbol = myCategory.symbol().clone()
                myStylesList.append(mySymbol)
        elif myType == 'graduatedSymbol':
            for myRange in myRenderer.ranges():
                mySymbol = myRange.symbol().clone()
                myStylesList.append(mySymbol)
        else:
            myMessage = 'Unknown symbol type.'
            raise Exception(myMessage)
        return myStylesList

    def getClickBbox(self, thePoint):
        """
        Get a tiny bbox around a mouse click.

        Args:
            Point object.
        Returns:
            Tiny QgsRectangle bbox around point.
        Raises:
            Exception if bbox creation encounters error.
        """
        # get the xy coords
        print (thePoint)
        myX = thePoint.x()
        myY = thePoint.y()

        # create a little bbox from clicked coords
        try:
            myBbox = QgsRectangle()
            myBbox.setXMinimum(myX - 1)
            myBbox.setYMinimum(myY - 1)
            myBbox.setXMaximum(myX + 1)
            myBbox.setYMaximum(myY + 1)
            return myBbox
        except:
            msg = 'Click coordinates could not be processed.'
            raise Exception(msg)

    def pixelToCrsBox(self, theClickBox, theCanvas, theLayer):
        """
        Takes a bbox in pixel coords, converts it to a bbox in layer coords.

        Args:
            The bbox that needs to be converted.
            The current canvas.
            The current layer.
        Returns:
            The converted bbox.
        Raises:
            None
        """
        # converts from screen to map canvas crs
        myMapToPixel = theCanvas.getCoordinateTransform()
        myX1 = theClickBox.xMinimum()
        myY1 = theClickBox.yMinimum()
        myPoint1 = myMapToPixel.toMapCoordinates(myX1, myY1)

        myX2 = theClickBox.xMaximum()
        myY2 = theClickBox.yMaximum()
        myPoint2 = myMapToPixel.toMapCoordinates(myX2, myY2)

        myRectangle = QgsRectangle(myPoint1, myPoint2)

        # converts the click box from canvas crs to the layer's CRS
        myCanvasCrs = theCanvas.mapRenderer().destinationCrs()
        myLayerCrs = theLayer.crs()
        myTransform = QgsCoordinateTransform(myCanvasCrs, myLayerCrs)
        myExtent = myTransform.transform(myRectangle)
        return myExtent

    def getFirstFeature(self, theLayer, theExtent):
        """
        Gets the first feature within the bbox in the active layer.

        Args:
            The current layer.
            The converted bbox.
        Returns:
            A feature.
        Raises:
            Exception if data could not be loaded.
        """

        myProvider = theLayer.dataProvider()
        if myProvider is None:
            msg = ('Could not obtain data provider from '
               'layer "%s"' % theLayer.source())
            raise Exception(msg)

        #myLayerExtent = theLayer.extent()
        myAttributes = myProvider.attributeIndexes()
        myFetchGeometryFlag = True
        myUseIntersectFlag = True

        mySelection = myProvider.select(myAttributes,
                      theExtent, myFetchGeometryFlag, myUseIntersectFlag)
        print ('SELECTED: %s' % mySelection)
        myFeature = myProvider.nextFeature(mySelection)
        return myFeature

    def getStyleForFeature(self, theFeature):
        """
        Gets the class of the feature passed to it.

        Args:
            A feature.
        Returns:
            A class.
        Raises:
            None.
        """
        pass
