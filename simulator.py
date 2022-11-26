
from tkinter import *
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import os

def select_file(elem):

    filetypes = (
        ('lib files', '*.lib'),
        ('verilog files', '*.v')
    )

    filename = fd.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)
    if len(filename)>0:
        elem.set(filename)

def set_elem(root,elem,width,float=None,x=0,y=0,x_pad=10,y_pad=10,pos_below=None,pos_after=None):
    elem.pack()
    root.update()
    ewidth = elem.winfo_width()

    if float=='c':
        x = int((width-ewidth)/2)
    elif float=='l':
        x = x_pad
    elif float=='r':
        x=width-ewidth-x_pad
    
    if pos_below != None:
        y = pos_below.winfo_rooty()-pos_below.winfo_height()+y_pad
    
    if pos_after != None:
        x = pos_after.winfo_rootx()+pos_after.winfo_width()+x_pad
        

    elem.place(x=x, y=y)

def deselect_group(radio_list):
    for radio in radio_list:
        radio.deselect()

def extract_graph(msg,lib,src,fbr_val):
    if os.path.exists(lib)==False:
        msg.set("library path does not exists!!!")
        return None
    if os.path.exists(src)==False:
        msg.set("Verilog file path does not exists!!!")
        return None

if __name__ == "__main__":
    root = Tk()
    
    width=800
    height=600
    root.geometry(str(width)+'x'+str(height))
    
    label=Label(root, text= "BUET SAT Attack Simulator",font= ('Helvetica 18 underline bold'), foreground='purple1',pady=4)
    set_elem(root,label,width,float='c',y=10)

    #Add Library File
    txt1=Label(root, text= "Library File = ")
    set_elem(root,txt1,width,float='l',pos_below=label)
    url_lib = StringVar()
    E1 = Entry(root, width=50,textvariable=url_lib)
    url_lib.set("Enter the lib file path...")
    set_elem(root,E1,width,pos_below=label,pos_after=txt1)
    btn1 = Button(root, text = 'Select File', command=lambda: select_file(url_lib))
    set_elem(root,btn1,width,pos_below=label,pos_after=E1)

    #Add Synthesized Verilog File
    txt2=Label(root, text= "Verilog File = ")
    set_elem(root,txt2,width,float='l',pos_below=txt1)
    url_sf = StringVar()
    E2 = Entry(root, width=50,textvariable=url_sf)
    url_sf.set("Enter the Synthesized Verilog File path...")
    set_elem(root,E2,width,pos_below=txt1,pos_after=txt2)
    btn2 = Button(root, text = 'Select File', command=lambda: select_file(url_sf))
    set_elem(root,btn2,width,pos_below=txt1,pos_after=E2)
    
    #Add option for making graph file
    txt3=Label(root, text= "Feedback Loop Replace By :")
    set_elem(root,txt3,width,float='l',pos_below=txt2)
    fbr_val = IntVar()
    R1 = Radiobutton(root, text="0", variable=fbr_val, value=0,command=lambda: deselect_group([R2]))
    set_elem(root,R1,width,pos_below=txt2,pos_after=txt3)
    R2 = Radiobutton(root, text="1", variable=fbr_val, value=1,command=lambda: deselect_group([R1]))
    set_elem(root,R2,width,pos_below=txt2,pos_after=R1)

    #Extract button & Msg Box
    btn3 = Button(root, text = 'Extract Graph', command=lambda: extract_graph(msg_graph,url_lib.get(),url_sf.get(),fbr_val.get()))
    set_elem(root,btn3,width,float='l',pos_below=txt3)
    txt4=Label(root, text= "Execution Msg ->")
    set_elem(root,txt4,width,pos_below=txt3,pos_after=btn3,x_pad=50,y_pad=15)
    msg_graph = StringVar()
    E3 = Entry(root, width=50,textvariable=msg_graph)
    msg_graph.set("Etract Graph Operation Result Will Show Here...")
    set_elem(root,E3,width,pos_below=txt3,pos_after=txt4,x_pad=0,y_pad=15)
    root.mainloop()


""" master = Tk()
    w = Canvas(master, width=2500, height=2500)
    w.pack()
    var1 = IntVar()
    Checkbutton(w, text='male', variable=var1).grid(row=0,column=0)
    var2 = IntVar()
    Checkbutton(w, text='female', variable=var2).grid(row=1,column=0)
    Spinbox(w, from_ = 0, to = 10).grid(row=2,column=0)
    Button(w, text ="Hello", command = select_file).grid(row=3,column=0)
    mainloop() """