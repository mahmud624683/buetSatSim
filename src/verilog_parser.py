import re
import json
import os

synth_lib_path = ""

def get_gate_def():
    file_load = open(synth_lib_path, "r")
    def_lib = file_load.read()
    def_lib = def_lib.replace("\t","")
    def_lib = def_lib.replace("\n","")
    cells = def_lib.split("*/cell (")

    cell_dict = {}

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

        cell_dict[cell_name] = {"inpin":inpin,"outpin":outpin,"function":gate_func}
    return cell_dict

def module_begin_end(code_line):
    code_line=code_line.lower()
    if code_line.find("module")>=0:
        return True
    elif code_line.find("endmodule")>=0:
        return True
    return False

def get_tag_number(code_linex):
    code_line=code_linex.lower()
    if code_line.find("input")>=0:
        start=code_line.find("input")+5
        tag=1
    elif code_line.find("output")>=0:
        start=code_line.find("output")+6
        tag=2
    elif code_line.find("wire")>=0:
        return 0,""
    elif code_line.find("assign")>=0:
        start=code_line.find("assign")+6
        tag=3
    elif code_line.find("dff")>=0:
        return 4,code_linex.strip()
    elif code_line.find("dlh")>=0:
        return 5,code_linex.strip()
    else:
        return 6,code_linex.strip()

    temp=code_linex[start:-1]+code_linex[-1]
    temp=temp.replace(" ","")
    templist=temp.split(",")
    #print(templist)
    return tag,templist

def get_range(temp_data):
    temp_data=temp_data.replace("[","")
    temp_data=temp_data.replace("]","")
    temp_range=temp_data.split(":")
    start=int(temp_range[0])
    end=int(temp_range[1])
    if(start>end):
        temp_val=end
        end=start
        start=temp_val
    return start,end

#each node of node tree = [input, date type, output, function, flag, level, value]

def get_circuit_graph(code_lines):
    def_dict=get_gate_def()
    flag=False
    node_tree={}
    for x in code_lines:
        if flag:
            #print(x)
            if module_begin_end(x):
                break
            tag_number,datum=get_tag_number(x)
            if tag_number==1:
                for data in datum:
                    if data.find(":")>=0:
                        temp_data=data.split("]")
                        if len(temp_data[0])>2:
                            data=temp_data[1]
                            start,end=get_range(temp_data[0])
                        else:
                            temp_data=data.split("[")
                            data=temp_data[0]
                            start,end=get_range(temp_data[1])
                        for i in range(start,end+1):
                            node_tree[data+"["+str(i)+"]"]=[[],"input",[],"",0,0,0]

                    else: 
                        node_tree[data]=[[],"input",[],"",0,0,0]

            elif tag_number==2:
                for data in datum:
                    if data.find(":")>=0:
                        temp_data=data.split("]")
                        if len(temp_data[0])>2:
                            data=temp_data[1]
                            start,end=get_range(temp_data[0])
                        else:
                            temp_data=data.split("[")
                            data=temp_data[0]
                            start,end=get_range(temp_data[1])
                        for i in range(start,end+1):
                            out_name = data+"["+str(i)+"]"
                            node_tree[out_name+"_reg"]=[[out_name],"output",[],out_name,0,0,0]

                    else: 
                        node_tree[data+"_reg"]=[[data],"output",[],data,0,0,0]
            elif tag_number==3:
                data = datum[0].split("=")
                if "'b" in data[1]:
                    node_tree[data[0]]=[[],"assign",[],int(data[1].split("'b")[1]),0,0,0]  
                else:
                    node_tree[data[0]]=[[data[1]],"assign",[],data[1],0,0,0]
            elif tag_number:
                result = re.search('\((.*)\)', datum)
                io_list=(result.group(1)).split(",")
                input_list=[]
                out_list=[]
                func_list=[]
                node_type=datum.split(" ")[0]
                temp_io=def_dict[node_type]
                in_def={}

                #searching input pin, output pin and function
                for i in range(0,len(io_list)):
                    pin_name= (io_list[i].strip()).split(" ")[0]
                    pin_name=pin_name.replace(".","")
                    pin_name=pin_name.strip()
                    xresult = re.search('\((.*)\)', io_list[i])
                    temp_result=xresult.group(1)
                    if "'b" in temp_result:
                        temp_result = int(temp_result.split("'b")[1])
                    if pin_name in temp_io["inpin"]:
                        input_list.append(temp_result)
                        in_def[pin_name]=temp_result
                    elif temp_result.find("UNCONNECTED")==-1:
                        out_list.append(temp_result)
                        out_index = temp_io["outpin"].index(pin_name)
                        func_list.append(temp_io["function"][out_index])
                
                #searching function
                for i in range(0,len(func_list)):
                    temp_func=func_list[i]
                    variables = re.findall("[A-Za-z0-9]+", temp_func)
                    for var in variables:
                        stx = r"\b"+var+r"\b"
                        mlist = []
                        for match in re.finditer(stx, temp_func):
                            s = match.start()
                            e = match.end()
                            mlist.append([s,e])

                        for s in reversed(mlist):
                            temp_func= str(in_def[var]).join([temp_func[:s[0]],temp_func[s[1]:]])
                        
                    func_list[i] = temp_func
                
                for i in range(0,len(out_list)):
                    node_name = out_list[i]
                    if node_name+"_reg" in node_tree.keys(): 
                        node_tree[node_name]=[input_list,node_type,[node_name+"_reg"],func_list[i],0,0,0]
                    elif node_name in node_tree.keys():
                        input_list=input_list+(node_tree[node_name])[0]
                        output_list=(node_tree[node_name])[2]
                        node_tree[node_name]=[input_list,node_type,output_list,func_list[i],0,0,0]
                    else: 
                        node_tree[node_name]=[input_list,node_type,[],func_list[i],0,0,0]
                
                    #update existing node
                    for x in input_list:
                        if x in node_tree.keys(): 
                            output=(node_tree[x])[2]
                            output.append(node_name)
                            (node_tree[x])[2]=output
                        elif (type(x)!=int) & (str(x).strip !=""):
                            node_tree[x]=[[],"",[node_name],"",0,0,0]

        elif module_begin_end(x):
            flag=True
    return node_tree
#each node of node tree = [input,date type, output, function, flag, level,value]

def get_in_out_lvl(circuit_def):
    dict_keys = circuit_def.keys()
    Lo=[]
    for x in dict_keys:
        if circuit_def[x][1]=="output":
            Lo.append(x)
    return Lo

def set_lvl(tree,node):
    if tree[node][1] == "input":
        tree[node][4] = -1
        return 0 
    elif tree[node][4] == -1:
        return tree[node][5]
    elif tree[node][4] > 0:
        return 0
    else:
        inlist = tree[node][0]
        for inpin in inlist:
            tree[node][4] += 1
            if type(inpin)==int:
                lvl = 0
            else: 
                lvl = set_lvl(tree,inpin)
            if lvl>=tree[node][5]:
                tree[node][5] = lvl+1
        tree[node][4] = -1
        return tree[node][5]   


def set_gate_lvl(circuit_def):
    lo = get_in_out_lvl(circuit_def)
    for outpin in lo:
        lvl = set_lvl(circuit_def,outpin)
        circuit_def[outpin][5] = lvl+1
        circuit_def[outpin][4] = -1
    unmap_node = get_unmapped(circuit_def)
    #print(unmap_node)
    #node = "n_73"
    for node in unmap_node:
        if "K" not in node:
            if circuit_def[node][1] == "input":
                if len(circuit_def[node][2]) == 0:
                    circuit_def[node][5] = -1
            else:
                circuit_def[node][5] = -1

    return circuit_def

def check_mapping(circuit_def):
    flag = 0
    dict_keys = circuit_def.keys()   
    for x in dict_keys:
        if circuit_def[x][4]!= -1:
            flag += 1
            print(circuit_def[x])
            """ if flag==10:
                break """
    return flag
def get_unmapped(circuit_def):
    unmapped=[]
    dict_keys = circuit_def.keys()   
    for x in dict_keys:
        if circuit_def[x][4]== 0:
            unmapped.append(x)
    return unmapped

def parser(file_path,lib_path):
    global synth_lib_path 
    synth_lib_path = lib_path
    file_load = open(file_path, "r")
    code = file_load.read()
    code = code.replace("\n"," ")
    output_graph = get_circuit_graph(code.split(";"))
    output_graph = set_gate_lvl(output_graph)
    file_path = file_path.split("/")[-1]
    file_path = file_path.split("\\")[-1]
    file_path = os.path.join("files",file_path)
    #print("Number of level-free node = " + str(check_mapping(output_graph)))
    with open(file_path.replace(".","_")+'.json', 'w') as fp:
            json.dump(output_graph, fp)
    
