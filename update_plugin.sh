QGIS_PLUGIN=~/.qgis/python/plugins/BucketFill
rm *.*~ *~ *.pyc
sudo rm -r $QGIS_PLUGIN
mkdir $QGIS_PLUGIN
cp -r gui/* $QGIS_PLUGIN
