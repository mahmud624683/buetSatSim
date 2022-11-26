import re

#each node of node tree = [input,date type, output, function, flag, level,value]
def map_circuit(circuit_def):
    ckt_map = [[],[]]
    dict_keys = circuit_def.keys()
    
    for x in dict_keys:
        key = circuit_def[x][5]
        if key >= 0:
            if key >= len(ckt_map):
                for i in range(len(ckt_map),key+1):
                    ckt_map.append([])
            ckt_map[key].append(x)
    return ckt_map

def get_output_nodelist(circuit_def):
    dict_keys = circuit_def.keys()
    Lo=[]
    for x in dict_keys:
        if circuit_def[x][1]=="output":
            Lo.append(x)
    return Lo

def reset_ckt(circuit_def,val=0):
    dict_keys = circuit_def.keys()
    for x in dict_keys:
        circuit_def[x][6] = val
    return circuit_def

def eval_node(circuit_def, key):
    #print(key)
    func = circuit_def[key][3]
    inputs = {}
    #print(circuit_def[key])
    for x in circuit_def[key][0]:
        if type(x)==int:
            node_val = x
            x = str(x)
        else: 
            node_val = circuit_def[x][6]
        stx = r"\b"+x+r"\b"
        mlist = []
        for match in re.finditer(stx, func):
            s = match.start()
            e = match.end()
            mlist.append([s,e])

        for s in reversed(mlist):
            func= str(node_val).join([func[:s[0]],func[s[1]:]])
                
    #print(func)
    val = eval(str(func))
    if val<0:
        val +=2
    circuit_def[key][6] = val
    return val

def set_input(ckt_def,in_nodes,value=None):
    if type(in_nodes)==list:
        for i in range(0,len(value)):
            node = in_nodes[i]
            ckt_def[node][6] = int(value[i])
    else:
        dict_keys = in_nodes.keys()
        for node in dict_keys:
            ckt_def[node][6] = int(in_nodes[node])

def get_output(ckt_def,nodes):
    output={}
    for outpin in nodes:
        output[outpin] = ckt_def[outpin][6]
    return output

def eval_circuit(ckt_def,ckt_map,lo=None):
    for i in range(1,len(ckt_map)):
        lvl_gates = ckt_map[i]
        for node in lvl_gates:
            eval_node(ckt_def,node)
    if lo==None:
        return get_output(ckt_def,ckt_map[-1])
    else:
        return get_output(ckt_def,lo)
