"""QGIS Singleton Application for use with Unit Tests.

Contact : tim@linfiniti.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '30/01/2011'
__copyright__ = 'Copyright 2012, Linfiniti Consulting CC.'

import os
import sys
from qgis import core
from qgis.core import QgsApplication

QGISAPP = None  # Static variable used to hold hand to running QGis app


def globalQgis():
    """Singleton implementation for a global QGIS app instance.

    Args:
        None
    Returns:
        A QGIS Application instance
    Raises:
        None
    """

    global QGISAPP

    if QGISAPP is None:
        myGuiFlag = True  # All test will run qgis in gui mode
        QGISAPP = QgsApplication(sys.argv, myGuiFlag)
        if 'QGISPATH' in os.environ:
            myPath = os.environ['QGISPATH']
            myUseDefaultPathFlag = True
            QGISAPP.setPrefixPath(myPath, myUseDefaultPathFlag)

        QGISAPP.initQgis()
        s = QGISAPP.showSettings()
        print s
    return QGISAPP
