import hou

def find_node_in_geo(sopNode, targetName, delete=False):
    geoNodePath = sopNode.path()
    secondSlashIndex = geoNodePath.index("/", geoNodePath.index("/", geoNodePath.index("/") + 1) + 1)
    geoNodePath = geoNodePath[0:secondSlashIndex]
    node_to_find = [child for child in hou.node(geoNodePath).allSubChildren() if child.name() == targetName]
    if node_to_find and delete:
        node_to_find[0].destroy()
        return True
    elif node_to_find:
        return node_to_find[0]
    else:
        return False


def find_node_in_context(targetName, context,delete=False ):
    startPath = context
    node_to_find = [child for child in hou.node(startPath).allSubChildren() if child.name() == targetName]
    if node_to_find and delete:
        node_to_find[0].destroy()
        return True
    elif node_to_find:
        return node_to_find[0]
    else:
        return False

#create null node which guides id map rendering
def create_and_wire_outnull(sopNode, nodeName):
    new_FON = sopNode.createOutputNode('null')
    new_FON.setName(nodeName)
    fon_parm_group = new_FON.parmTemplateGroup()
    folder_in_null = hou.FolderParmTemplate("folder","ID map")
    render_path = hou.StringParmTemplate("path_str","Save Folder",1)
    render_path.setDefaultValue("$HIP/render/bake.png")
    mplay_button = hou.ButtonParmTemplate("mplay_btn_id","Texture in MPlay")
    mplay_button.setScriptCallback("opparm -c /out/mei_bake_id renderpreview")
    render_button = hou.ButtonParmTemplate("execute_btn_id", "Render to Disk")
    render_button.setScriptCallback("opparm -c /out/mei_bake_id execute")
    folder_in_null.addParmTemplate(render_path)
    folder_in_null.addParmTemplate(mplay_button)
    folder_in_null.addParmTemplate(render_button)
    fon_parm_group.append(folder_in_null)
    new_FON.setParmTemplateGroup(fon_parm_group)
    new_FON.setParms({"path_str":"$HIP/render/bake.png"})
    return new_FON


def InsertAfterNode(existed_node, node_to_insert):
    curr_connected_nodes = list(existed_node.outputs())
    curr_connected_nodes.remove(node_to_insert)
    # find the indexs of the connection of the original node, since attribute create node has only one output, so just connect to the first one after
    connectionsTuple = [node.inputConnections() for node in curr_connected_nodes]
    validConnectionIndexs = [connection.inputIndex() for connections_on_node in connectionsTuple for connection in
                             connections_on_node if connection.inputNode() == existed_node]
    for nodeorder, node in enumerate(curr_connected_nodes):
        node.setInput(validConnectionIndexs[nodeorder], node_to_insert, 0)
    node_to_insert.moveToGoodPosition()


def find_global_attribs_with_prefix(node, prefix):
    geo = node.geometry()
    validAttribis = [attrib for attrib in geo.globalAttribs() if attrib.name().startswith(prefix)]
    values = [geo.attribValue(attrib.name()) for attrib in validAttribis if geo.attribValue(attrib.name())!="REMOVED"]
    values = list(set(values))
    return values

#creates nodes in mat and out context
def create_texture_bake_attrib(sopNode,attrib,node_name,fon_path):
    outNode = hou.node("/out")
    bakeNode = outNode.createNode("baketexture")
    obj_path = get_node_geo(sopNode)
    bakeNode.setParms({'vm_uvobject1':obj_path,
                       "vm_numaux":1,
                       "vm_variable_plane1":attrib,
                       "vm_extractimageplanesformat":"PNG",
                       "vm_uvoutputpicture1":"`chs(\"{0}/path_str\")`".format(fon_path)})
    bakeNode.setName(node_name)
    mat_bake = hou.node("/mat/").createNode("meiHoudiniTools_mei_bake_id")
    mat_bake.setParms({'attribname':attrib})
    hou.node(obj_path).setParms({"shop_materialpath":mat_bake.path()})

def get_node_geo(node):
    nodePath = node.path()
    secondSlashIndex = nodePath.index("/", nodePath.index("/", nodePath.index("/") + 1) + 1)
    context_path = nodePath[0:secondSlashIndex]
    return context_path
