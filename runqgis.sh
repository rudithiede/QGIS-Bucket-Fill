#!/bin/bash
export QGISPATH=/home/rudi/apps/qgis-1_8
export PYTHONPATH=$PYTHONPATH:/home/rudi/apps/qgis-1_8/share/qgis/python/
export PYTHONPATH=$PYTHONPATH:/home/rudi/.eclipse/org.eclipse.platform_3.7.0_155965261/plugins/org.python.pydev.debug_2.3.0.2011121518/pysrc/
/home/rudi/apps/qgis-1_8/bin/qgis /home/rudi/.qgis/python/plugins/VectorBucketFill/test_data/test.shp
