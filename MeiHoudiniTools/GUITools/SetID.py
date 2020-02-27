import hou
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
from random import choice

from MeiHoudiniTools.NoGUITools import FindNode

reload(FindNode)


class SetIDMainWnD(QtWidgets.QWidget):
    def __init__(self, nodeToAdd):
        super(SetIDMainWnD, self).__init__()
        self.setWindowTitle("Set a new ID to prims")
        self.finalAttribCreate = FindNode.find_node_in_geo(nodeToAdd, "mei_id_attrib_final")
        self.nodeToAdd = nodeToAdd
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
        # self.existedGlobalAttrib = nodeToAdd.globalAttribs()

    def create_widgets(self):
        # Color related Widgets
        self.color_button = hou.qt.ColorSwatchButton()
        self.color_in_hex = QtWidgets.QLineEdit()
        self.color_in_hex_label = QtWidgets.QLabel("Color in HEX:")
        self.select_color_label = QtWidgets.QLabel("Press to change default random color")
        self.used_color_label = QtWidgets.QLabel("Used id in geo:")
        self.used_color_combobox = hou.qt.ComboBox()
        # Infomation related Widgets
        self.output_path = QtWidgets.QLabel("Final attrib create found at: " + self.finalAttribCreate.path())
        # Command related Widgets
        self.confirm_button = QtWidgets.QPushButton("OK")
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        # Group Selection
        self.groupLabel = QtWidgets.QLabel("Select Groups")
        self.groupEdit = QtWidgets.QLineEdit()
        self.groupCombobox = hou.qt.ComboBox()
        # self.groupCombobox.setFixedWidth(20)
        self.geoGroupList = [""] + [group.name() for group in self.nodeToAdd.geometry().primGroups()]
        self.groupCombobox.addItems(self.geoGroupList)

    def create_layouts(self):
        # Group selection
        groupSelection = QtWidgets.QHBoxLayout()
        groupSelection.addWidget(self.groupLabel)
        groupSelection.addWidget(self.groupEdit)
        groupSelection.addWidget(self.groupCombobox)
        # color layout
        color_pick_layout = QtWidgets.QHBoxLayout()
        color_pick_layout.addWidget(self.select_color_label)
        color_pick_layout.addWidget(self.color_button)
        color_pick_layout.addWidget(self.color_in_hex_label)
        color_pick_layout.addWidget(self.color_in_hex)
        # automatically pick a new color from pool
        currInsColor = self.get_new_random_id_color()
        self.color_button.setColor(currInsColor[0])
        self.pick_color_with_qt()
        # pick a color used in the same geo with a combobox
        color_pick_layout.addWidget(self.used_color_label)
        color_pick_layout.addWidget(self.used_color_combobox)
        self.used_color =[""] + FindNode.find_global_attribs_with_prefix(self.finalAttribCreate, "id")
        self.used_color_combobox.addItems(self.used_color)

        info_layout = QtWidgets.QHBoxLayout()
        info_layout.addWidget(self.output_path)
        info_layout.addStretch()

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(groupSelection)
        main_layout.addLayout(color_pick_layout)
        main_layout.addLayout(info_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        # Change the color of text when button color changed
        self.color_button.colorChanged.connect(self.pick_color_with_qt)
        # Quit button
        self.cancel_button.clicked.connect(self.close)
        # Call the function that creates attribcreate node
        self.confirm_button.clicked.connect(self.create_color)
        # change the content of groups editline after selecting
        self.groupCombobox.activated.connect(self.change_group_edit)
        # change the color when manually edit the hex string
        self.color_in_hex.textChanged.connect(self.change_button_color)
        # change the color when select a used color that is not none
        self.used_color_combobox.activated.connect(self.select_used_color)

    def select_used_color(self,box_index):
        self.color_in_hex.setText(self.used_color[box_index])

    def change_button_color(self, new_text):
        self.color_button.setColor(QtGui.QColor(new_text))

    def change_group_edit(self, boxIndex):
        textToSet = self.groupEdit.text() + " " + self.geoGroupList[boxIndex] \
            if self.groupEdit.text().find(self.geoGroupList[boxIndex]) == -1 else self.groupEdit.text()
        self.groupEdit.setText(textToSet)

    def pick_color_with_qt(self):
        # QColor is not normalized, max 255
        self.selected_color = self.color_button.color()
        self.color_in_hex.setText(self.selected_color.name())

    def create_id(self, color):
        pass

    # Called when press confirm
    def create_color(self):
        #correct the selected color
        self.selected_color = self.color_button.color()
        # create attrib node info
        attrib_wrangle_node = self.nodeToAdd.createOutputNode('attribwrangle')
        FindNode.InsertAfterNode(self.nodeToAdd, attrib_wrangle_node)
        attrib_wrangle_node.setName("mei_add_id", True)
        # Normalize color to fixed3
        normalizedColor = [self.selected_color.red() / 255.0, self.selected_color.green() / 255.0,
                           self.selected_color.blue() / 255.0]
        attrib_wrangle_node.setParms({"group": self.groupEdit.text(),
                                      "class": 1,
                                      "snippet": '''int existed;
vector currid = primattrib(0,'id',@primnum,existed);
if(existed==0 || currid == {{-1,-1,-1}}){{
v@id = {{{0},{1},{2}}};
}}'''.format(normalizedColor[0], normalizedColor[1], normalizedColor[2])})
        # add a folder to attrib node
        currentParmNumber = int(self.finalAttribCreate.parm("numattr").eval()) + 1
        parm_group = attrib_wrangle_node.parmTemplateGroup()
        folder_to_add = hou.FolderParmTemplate("folder", "mei_do_not_modify")
        folder_to_add.addParmTemplate(hou.StringParmTemplate("hxcolor", "Color in Hex", 1))
        folder_to_add.addParmTemplate(hou.IntParmTemplate("colorparmindex", "Color Index", 1))
        parm_group.append(folder_to_add)
        attrib_wrangle_node.setParmTemplateGroup(parm_group)
        attrib_wrangle_node.setParms({'hxcolor': self.color_in_hex.text(), 'colorparmindex': (currentParmNumber - 1)})
        # extend the attrib capacity by 1 and add the new color to it
        self.finalAttribCreate.setParms({'numattr': currentParmNumber})
        self.finalAttribCreate.setParms({"name" + str(currentParmNumber): "id" + str(currentParmNumber),
                                         "class" + str(currentParmNumber): 0,
                                         "type" + str(currentParmNumber): 3,
                                         "string" + str(currentParmNumber): self.color_in_hex.text()})
        # set the delete action, because of the index issue, the deleted one were set to zero instead of removed from
        # the list so no need to iterate over the all the attribcreate nodes
        finalPath = self.finalAttribCreate.path()
        calledwhendelete = 'opparm -C {0} string{1} \'REMOVED\''.format(finalPath, currentParmNumber)
        attrib_wrangle_node.setDeleteScript(calledwhendelete, hou.scriptLanguage.Hscript)
        self.close()

    def get_new_random_id_color(self):
        IDColorGroup = ['#ff8000', '#ffff00', '#80ff00', '#00ff80', '#00ffff', '#0080ff', '#0000ff',
                        '#8000ff', '#ff00ff', '#ff0000', '#00ff00', '#80ff80','#ff80ff']
        existedColor = FindNode.find_global_attribs_with_prefix(self.finalAttribCreate, "id")
        color_to_select = choice([color for color in IDColorGroup if not color in existedColor])
        this_color = QtGui.QColor(color_to_select)
        # print(existedColor)
        return (this_color, color_to_select)
        pass


class SelectedNodeWrongWnD(QtWidgets.QWidget):
    def __init__(self, ErrorInfomation="Please select a single sop node!"):
        super(SelectedNodeWrongWnD, self).__init__()
        self.error_info = ErrorInfomation
        self.setWindowTitle("Node Error")
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)

    def create_widgets(self):
        self.ErrorInfo = QtWidgets.QLabel(self.error_info)
        self.confirm = QtWidgets.QPushButton("OK")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.ErrorInfo)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.confirm)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.confirm.clicked.connect(self.close)


class ExistedFOPWnD(QtWidgets.QWidget):
    def __init__(self):
        super(ExistedFOPWnD, self).__init__()
        self.setWindowTitle("Node Existed")
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)

    def create_widgets(self):
        self.error_info = QtWidgets.QLabel("Existed final output detected, please choose an option")
        self.replace_button = QtWidgets.QPushButton("Replace it")
        self.replace_button = QtWidgets.QPushButton("Move here")
        self.calcel_button = QtWidgets.QPushButton("Cancel")

    def create_layouts(self):
        pass

    def create_connections(self):
        pass


def create_id_window():
    selectedNode = hou.selectedNodes()
    if not FindNode.find_node_in_geo(selectedNode[0], "mei_final_output"):
        errWnd = SelectedNodeWrongWnD("Please create a new output with tool before adding IDs")
        errWnd.show()
    elif (len(selectedNode) == 0):
        errWnD = SelectedNodeWrongWnD()
        errWnD.show()
    elif (len(selectedNode) == 1 and str(selectedNode[0].type().category()) == "<hou.NodeTypeCategory for Sop>"):
        IDWnD = SetIDMainWnD(selectedNode[0])
        IDWnD.show()
    else:
        errWnD = SelectedNodeWrongWnD()
        errWnD.show()


def hex_to_color(HexColor):
    # return '#'+''.join([hex(int(channel*255.0)).split('x')[-1] for channel in color.rgb()])
    colotTuple = tuple(int(HexColor[i:i + 2], 16) for i in (1, 3, 5))
    return QtGui.QColor(HexColor)
