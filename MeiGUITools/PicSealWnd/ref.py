from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr),QtWidgets.QWidget)

class TestDialog(QtWidgets.QDialog):
    def __init__(self,parent = maya_main_window()):
        super(TestDialog, self).__init__(parent)
        self.setWindowTitle("Test Dialog")
        self.setMinimumWidth(200)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
    def create_widgets(self):
        self.combobox = QtWidgets.QComboBox()
        self.combobox.addItems(["ComboItem 1","ComboItem 2","ComboItem 3"])
        self.lineedit = QtWidgets.QLineEdit()
        self.checkbox1 = QtWidgets.QCheckBox("Checkbox1")
        self.checkbox2 = QtWidgets.QCheckBox("Checkbox2")
        self.ok_btn = QtWidgets.QPushButton("OK")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
    
    def create_layouts(self):
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("ComboBox",self.combobox)
        form_layout.addRow("Name:",self.lineedit)
        form_layout.addRow("Locked:",self.checkbox1)
        form_layout.addRow("Hidden:",self.checkbox2)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        
    def create_connections(self):
        self.cancel_btn.clicked.connect(self.close)
        self.lineedit.textChanged.connect(self.print_hello_name)
        self.checkbox1.toggled.connect(self.print_is_hidden)
        
    def print_hello_name(self,name):
        #name = self.lineedit.text()
        print("{0} hello!".format(name))
        
    def print_is_hidden(self,c):
        if c:
            print("Hidden")
        else:
            print("Visible")
if __name__ == "__main__":
    
    try:
        test_dialog.close()
        test_dialog.deleteLater()
    except:
        pass
    
    test_dialog = TestDialog()
    test_dialog.show()
