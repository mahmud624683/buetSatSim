import re
import json
import os

def __readlib(lib_path):
    file_load = open(lib_path, "r")
    def_lib = file_load.read()
    def_lib = def_lib.replace("\t","")
    def_lib = def_lib.replace("\n","")
    cells = def_lib.split("*/cell (")

    node_def = {}
    for i in range(1,len(cells)):
        cell = cells[i].split(") {")
        cell_name = cell[0]
        IQ = "D"
        IQN = "~D"
        fflag = ("latch (" in cells[i]) | ("ff (" in cells[i])
        #print(cell_name)
        inpin = []
        outpin = [] 
        gate_func = []
        pins = cells[i].split("pin (")
        for j in range(1,len(pins)):
            pin = pins[j].split(") {")
            pin_name = pin[0]
            #print(pin_name)
            temp = pin[1].split("direction:")[1]
            direction = temp.split(";")[0].strip()
            #print(direction)
            if (direction == "output"):
                temp = pin[1].split("function:")[1]
                function = temp.split(";")[0].strip()
                function = function.replace('"',"")
                function = function.replace("!","~")
                if fflag:
                    function = eval(function)
                #print(function)
                gate_func.append(function)
                outpin.append(pin_name)
            else: 
                inpin.append(pin_name)

        node_def[cell_name] = {"inpin":inpin,"outpin":outpin,"function":gate_func}
    return node_def

def __buildGraph(file_path,lib_path,init_val):
    nodes_def = __readlib(lib_path)
    file_load = open(file_path, "r")
    code = file_load.read()
    code = code.replace("\n"," ")
    statements = code.split(';')
    node_names = list(nodes_def.keys())+['input','output','assign']
    node_tree = {}
    node_tree['assign_1'] = {'in_link':[],'out_link':[],'val_func':'','value':1}
    node_tree['assign_0'] = {'in_link':[],'out_link':[],'val_func':'','value':0}

    for statement in statements:
        statement= statement.strip()
        node_type = statement.split(" ")[0]
        if node_type in node_names:
            
            if node_type == 'input':
                temp_node_des={'in_link':[],'out_link':[],'val_func':'','value':init_val}
                node_list = statement.replace("input","").strip().split(',')
                temp_node_des['val_func']='in'
                for node in node_list:
                    node_tree[node] = temp_node_des
            
            elif node_type == 'output':
                temp_node_des={'in_link':[],'out_link':[],'val_func':'','value':init_val}
                node_list = statement.replace("output","").strip().split(',')
                temp_node_des['val_func']='out'
                for node in node_list:
                    node_tree[node] = temp_node_des
            else:
                node_def = nodes_def[node_type]
                statement = statement.replace(" ","")
                pins = re.findall(r'\.[A-Za-z0-9]+\([A-Za-z0-9_]+\)',statement)
                inpins={}
                outpins={}
                for pin in pins:
                    pin_name,pin_con = pin.split('(')
                    pin_name = pin_name.replace('.','')
                    pin_con = pin_con.replace(')','')
                    if pin_name in node_def['inpin']:
                        inpins[pin_name]=pin_con
                    elif pin_name in node_def['outpin']:
                        outpins[pin_name]=pin_con
                for key in outpins.keys():
                    index = node_def['outpin'].index(key)
                    func = node_def['function'][index]
                    inlink=re.findall(r'[A-Za-z0-9]+',func)
                    for pin in inlink:
                        func = func.replace(pin,inpins[pin])
                    inlink=re.findall(r'[A-Za-z0-9]+',func)
                    ##fgfdgdg
                    node_tree[outpins[key]]={'in_link':inlink,'out_link':[],'val_func':func,'value':init_val}

    print('rend')
    return None
            



__buildGraph('s27_synth.v','nangate_typical.lib',0)
