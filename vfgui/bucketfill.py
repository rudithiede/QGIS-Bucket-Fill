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
from PyQt4.QtCore import QObject, SIGNAL, QSettings
from PyQt4.QtGui import QAction, QIcon, QColorDialog, QColor
from PyQt4.QtGui import QMessageBox
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsRectangle
from qgis.core import QgsPoint
from qgis.core import QgsMapLayer
from qgis.core import QgsCoordinateTransform
from qgis.gui import QgsRubberBand

# Initialize Qt resources from file resources.py dont remove this line even
# though it is marked as unused in eclipse
import resources
import custom_exceptions as ex

#see if we can import pydev - see development docs for details
try:
    from pydevd import *
    print 'Remote debugging is enabled.'
    DEBUG = True
except Exception, e:
    print 'Debugging was disabled.'


class BucketFill:
    """A little plugin to allow you to set the color of a vector
    class by clicking on it."""
    def __init__(self, IFACE):
        # Save reference to the QGIS interface
        self.iface = IFACE
        self.canvas = self.iface.mapCanvas()
        self.bucketTool = QgsMapToolEmitPoint(self.canvas)
        self.polygonFlag = True
        self.rubberband = QgsRubberBand(self.canvas,
                                        self.polygonFlag)

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
        self.iface.addToolBarIcon(self.colorChooserAction)
        self.iface.addPluginToMenu("&Bucket fill", self.colorChooserAction)
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
        self.colorChooserAction = (QAction(
                    QIcon(":/plugins/bucketfill/icon.png"),
                    "Bucket fill", self.iface.mainWindow()))
        self.bucketFillAction = (QAction(
                    QIcon(":/plugins/bucketfill/bucket.png"),
                    "Bucket fill", self.iface.mainWindow()))
        # connect the action to the chooseColor method
        QObject.connect(self.colorChooserAction,
                    SIGNAL("triggered()"), self.chooseColor)
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
        self.iface.removePluginMenu("&Bucket fill", self.colorChooserAction)
        self.iface.removeToolBarIcon(self.colorChooserAction)
        self.iface.removeToolBarIcon(self.bucketFillAction)

    def chooseColor(self):
        """Show a color picker to let the user choose a color.

        Args:
            None
        Returns:
            None
        Raises:
            None

        """
        mySettings = QSettings()
        try:
            myInitialColor = QColor(mySettings
                .value("vectorbucketfill/current_color"))
        except:
            myInitialColor = QColor(255, 255, 255)
        #myColor = QColor()
        myColor = QColorDialog.getColor(initial=myInitialColor)
        #myColorSelect = BucketFillDialog()
        if QColor.isValid(myColor):
            # do something useful
            mySettings.setValue("vectorbucketfill/current_color", myColor)

    def enableBucketTool(self):
        """Make the bucket tool active on the canvas.

        Args:
            None
        Returns:
            None
        Raises:
            None

        """
        self.canvas.setMapTool(self.bucketTool)

    def setColorForClass(self, thePoint, theButton):
        """Set the color of the active layer's feature
        class that falls under the cursor

        Args:

            * thePoint - a QgsPoint indicating where the click on
                the canvas took place in map coordinates of the canvas.
            * theButton - a Qt::MouseButton enumerator indicating
                which button was clicked with

        Returns:
            None
        Raises:
            None

        """
        # get the active layer
        myLayer = self.getActiveVectorLayer()

        # get style class list
        myStyles = self.getStyleClassList(myLayer)

        # identify click xy on canvas (map coords)
        myClickBox = self.getClickBbox(thePoint)
        # convert myClickBox to map coords
        #myExtent = self.pixelToCrsBox(myClickBox, self.canvas, myLayer)
        #settrace()
        # make a rubber band for visual confirmation of the click location
        myRubberBand = self.makeRubberBand(myClickBox)

        # use provider to select based on attr and bbox, and get first feature
        # from resulting list
        myFeature = self.getFirstFeature(myLayer, myClickBox)

        # find the symbol for said feature
        #mySymbol = self.getSymbolForFeature(myFeature)
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
            IncorrectLayerTypeException if current layer is not a vector layer
            NoCurrentLayerException if no layer is selected.
        """
        # get active layer for canvas
        myLayer = self.iface.activeLayer()
        if myLayer is None:
            myMessage = ('There is no current layer. Load a vector layer and '
                         'select it before using it.')
            raise ex.NoCurrentLayerException(myMessage)
        # check that it's a vector
        if myLayer.type() == QgsMapLayer.VectorLayer:
            return myLayer
        else:
            myMessage = 'Current layer is not a vector layer.'
            raise ex.IncorrectLayerTypeException(myMessage)

    def getStyleClassList(self, theLayer):
        """
        Get the list of style classes in the given layer.

        Args:
            Object: the active layer.
        Returns:
            A list of styles from the given layer.
        Raises:
            UnknownSymbolTypeException if symbol type is unknown.
            OldSymbologyException if layer uses old symbology.
        """
        if not theLayer.isUsingRendererV2():
            myMessage = ('This plugin does not currently'
                         ' support old symbology.')
            raise ex.OldSymbologyException(myMessage)

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
            raise ex.UnknownSymbolTypeException(myMessage)
        return myStylesList

    def getClickBbox(self, thePoint):
        """
        Get a tiny bbox around a mouse click.

        Args:
            Point object.
        Returns:
            Tiny QgsRectangle bbox around point.
        Raises:
            CoordinateProcessingException if bbox creation encounters error.
        """

        # get the xy coords
        #QMessageBox.information(None, 'VF', str(thePoint))
        myX = thePoint.x()
        myY = thePoint.y()
        myUnitsPerPixel = self.canvas.mapUnitsPerPixel()

        # create a little bbox from clicked coords
        try:
            myBbox = QgsRectangle()
            myBbox.setXMinimum(myX - myUnitsPerPixel)
            myBbox.setYMinimum(myY - myUnitsPerPixel)
            myBbox.setXMaximum(myX + myUnitsPerPixel)
            myBbox.setYMaximum(myY + myUnitsPerPixel)
            #QMessageBox.information(None, 'VF', myBbox.toString())
            return myBbox
        except:
            msg = 'Click coordinates could not be processed.'
            raise ex.CoordinateProcessingException(msg)

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

        myExtent = theCanvas.mapRenderer()\
            .mapToLayerCoordinates(theLayer, myRectangle)

        print "COMPUTED EXTENT: %s, %s, %s, %s" % (myExtent.xMinimum(),
                                                   myExtent.yMinimum(),
                                                   myExtent.xMaximum(),
                                                   myExtent.yMaximum())
        return myExtent

    def makeRubberBand(self, theRectangle):
        """Makes a rubber band select on the canvas where the user clicked."""
        self.rubberband.reset(True)
        self.rubberband = QgsRubberBand(self.canvas, True)
        self.rubberband.setColor(QColor(255, 0, 0))
        self.rubberband.setWidth(10)
        self.rubberband.addPoint(QgsPoint(\
                                          theRectangle.xMinimum(),
                                          theRectangle.yMinimum()))
        self.rubberband.addPoint(QgsPoint(\
                                          theRectangle.xMaximum(),
                                          theRectangle.yMinimum()))
        self.rubberband.addPoint(QgsPoint(\
                                          theRectangle.xMaximum(),
                                          theRectangle.yMaximum()))
        self.rubberband.addPoint(QgsPoint(\
                                          theRectangle.xMinimum(),
                                          theRectangle.yMaximum()))

    def getFirstFeature(self, theLayer, theClickBox):
        """
        Gets the first feature within the bbox in the active layer.

        Args:
            The current layer.
            The converted bbox.
        Returns:
            A feature.
        Raises:
            LayerLoadException if data could not be loaded.
            NoSelectedFeatureException if no feature is selected.
        """

        myProvider = theLayer.dataProvider()
        if myProvider is None:
            msg = ('Could not obtain data provider from '
               'layer "%s"' % theLayer.source())
            raise ex.LayerLoadException(msg)

        #myLayerExtent = theLayer.extent()
        myAttributes = myProvider.attributeIndexes()
        myFetchGeometryFlag = False
        myUseIntersectFlag = False

        QMessageBox.information(None, 'Provider', str(myProvider))
        QMessageBox.information(None, 'Box', str(theClickBox))
        self.rubberband.reset(True)
        mySelection = myProvider.select(myAttributes,
                      theClickBox, myFetchGeometryFlag, myUseIntersectFlag)

        if mySelection == None:
            raise ex.NoSelectedFeatureException(
                            "No feature selected. Using "
                            "provider {%s}, "
                            "attributes {%s}, and "
                            "rectangle {%s} with "
                            "extents {%s, %s, %s, %s}."
                            % (
                               str(myProvider),
                               str(myAttributes),
                               str(theClickBox),
                               theClickBox.xMinimum(),
                               theClickBox.yMinimum(),
                               theClickBox.xMaximum(),
                               theClickBox.yMaximum()
                             ))
        else:
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
