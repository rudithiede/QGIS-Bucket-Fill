# Logic from ZetCode PyGTK tutorial 
#
# author: jan bodnar
# website: zetcode.com 

import gtk


class Ui_BucketFill(gtk.Window): 
  def __init__(self):
    super(Ui_BucketFill, self).__init__()
    
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


Ui_BucketFill()
gtk.main()

"""
from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_BucketFill(object):
    def setupUi(self, BucketFill):
        BucketFill.setObjectName(_fromUtf8("BucketFill"))
        BucketFill.resize(219, 100)
        BucketFill.setWindowTitle(QtGui.QApplication.translate("BucketFill", "BucketFill", None, QtGui.QApplication.UnicodeUTF8))
        self.layoutWidget = QtGui.QWidget(BucketFill)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 178, 62))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setText(QtGui.QApplication.translate("BucketFill", "         Fill:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.kcolorbutton = KColorButton(self.layoutWidget)
        self.kcolorbutton.setColor(QtGui.QColor(255, 255, 255))
        self.kcolorbutton.setDefaultColor(QtGui.QColor(255, 255, 255))
        self.kcolorbutton.setObjectName(_fromUtf8("kcolorbutton"))
        self.gridLayout.addWidget(self.kcolorbutton, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.layoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 2)

        self.retranslateUi(BucketFill)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), BucketFill.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), BucketFill.reject)
        QtCore.QMetaObject.connectSlotsByName(BucketFill)

    def retranslateUi(self, BucketFill):
        pass

from PyKDE4.kdeui import KColorButton
"""
