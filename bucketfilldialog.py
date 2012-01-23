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
import gtk
# create the dialog for zoom to point
class BucketFillDialog(QtGui.QDialog):
  def __init__(self):
    #super(PyApp, self).__init__()
    #super(self).__init__()
    
    self.set_size_request(300, 150)
    self.set_position(gtk.WIN_POS_CENTER)
    self.connect("destroy", gtk.main_quit)
    self.set_title("Color Selection Dialog")
    
    
    self.label = gtk.Label("The only victory over love is flight.")
    button = gtk.Button("Select color")
    button.connect("clicked", self.on_clicked)

    fix = gtk.Fixed()
    fix.put(button, 100, 30)
    fix.put(self.label, 30, 90)
    self.add(fix)

    self.show_all()

  def on_clicked(self, widget):
    cdia = gtk.ColorSelectionDialog("Select color")
    response = cdia.run()
          
    if response == gtk.RESPONSE_OK:
      colorsel = cdia.colorsel
      color = colorsel.get_current_color()
      self.label.modify_fg(gtk.STATE_NORMAL, color)
    
    cdia.destroy()

#PyApp()
#gtk.main()

"""
  def __init__(self):
    QtGui.QDialog.__init__(self)
    # Set up the user interface from Designer.
    self.ui = Ui_BucketFill()
    self.ui.setupUi(self)
"""
