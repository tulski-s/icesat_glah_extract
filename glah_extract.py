import h5py
import os
import numpy as np
import time
from Tkinter import *
import ttk
import tkMessageBox
import tkFileDialog

my_FONT = ('Arial', '9')

def openfilesButton_OnClick():
    """
    Open one or multiple files and update Treeview
    """
    write_fileName()
    fill_hdf_tree()
    check_dataset_avaibility()

def opendirButton_OnClick():
    """
    Open all hdf5 files in chosen directory. Update Treeview
    """
    write_fileName_dir()
    fill_hdf_tree()
    check_dataset_avaibility()

def write_fileName():
    """
    Write name(s) of chosen file(s) to filesListBox.
    Change current working directory to place where files are located
    """
    filez = tkFileDialog.askopenfilenames(parent=app,title='Choose a file(s)')
    filez_as_list = list(app.tk.splitlist(filez))
    try:
        os.chdir(os.path.dirname(filez_as_list[0]))
        glah_type = h5py.File(os.path.basename(filez_as_list[0]), 'r').attrs['ShortName']
        filesListBox.delete(0, END)
        for mFile in filez_as_list:
            if h5py.File(mFile).attrs['ShortName'] != glah_type:
                tkMessageBox.showerror('Error','Different GLAH type fiels. You can add only GLAH files with the same type')
                return filesListBox.delete(0, END)
            else:
                filesListBox.insert(END, os.path.basename(mFile))
    except IndexError: pass
    except IOError: tkMessageBox.showerror('Error','Wrong input data type. It should be HDF')


def fill_hdf_tree():
    """
    Fill hdf tree
    """
    files_list = get_current_filesName()
    try:
        hdf = os.path.join(os.getcwd(),files_list[-1])
        if treeview.get_children():
            treeview.delete(treeview.get_children())
        create_root(treeview, hdf)
    except IndexError, KeyError:
        pass #they appears if no hdf in directory

def create_root(treeview, hdf_file):
    """
    Creates root of my TreeView
    """
    dfpath = h5py.File(hdf_file).attrs['ShortName']
    node = treeview.insert('', 'end', text=dfpath,
            values=[hdf_file.encode('string-escape'), 'root'], open=True)
    fill_tree(treeview, node, hdf_file)

def fill_tree(treeview, node, hdf_file):
    """
    Fills my Tree
    """
    f = h5py.File(hdf_file, 'r')

    if treeview.set(node, "type") == 'root':
        path = f

    elif treeview.set(node, "type") == 'Group':
        # value in node's fullpath is a string with group path inside quotation
        qm_pos = [i for i, j in enumerate(treeview.set(node, "fullpath"))if j == '"']
        group_path = treeview.set(node, "fullpath")[qm_pos[0]+1:qm_pos[1]]
        path = f[group_path]
        
    for p in sorted(path):
        ptype = None

        if type(path[p]).__name__ == 'Group':
            ptype = 'Group'
            img = G
        elif type(path[p]).__name__ == 'Dataset':
            ptype = 'Dataset'
            img = D

        oid = treeview.insert(node, 'end', text=p, image=img,
                              values=[path[p], ptype])
        
        if ptype == 'Group':
            fill_tree(treeview, oid, hdf_file)

def write_fileName_dir():
    """
    Write name(s) of file(s) which is(are) located in chosen directory to TEXT_field.
    Change current working directory to place where files are located
    """
    directory = tkFileDialog.askdirectory()
    try:
        os.chdir(str(directory))
        files = [mFile for mFile in os.listdir(os.getcwd()) if mFile.endswith('.H5')]
        glah_type = h5py.File(os.path.basename(files[0]), 'r').attrs['ShortName']
           
        filesListBox.delete(0, END)
        for mFile in files:
            if h5py.File(mFile).attrs['ShortName'] != glah_type:
                tkMessageBox.showerror('Error','Different GLAH type fiels. You can add only GLAH files with the same type')
                if treeview.get_children():
                    treeview.delete(treeview.get_children())
                return filesListBox.delete(0, END)
            else:
                filesListBox.insert(END, str(mFile))
    except OSError: pass
    except IOError:
        tkMessageBox.showerror('Error','Couldn\'t find any HDF file in this directory')
        return

def get_current_filesName():
    """
    Returns list of recently opened file(s)
    """

    if filesListBox.get(0,END)==[]: pass
    else:
        files_list = filesListBox.get(0,END)
        return files_list

def check_dataset_avaibility():
    """
    It checks if chosen dataset are available in GLAH file. If not it
    deletes chosenListBox.
    """
    files_list = get_current_filesName()
    if not files_list:
        return
    datasets=chosenListBox.get(0,END)
    if not datasets:
        return
    f=h5py.File(files_list[0], 'r')
    for dataset in datasets:
        try:
            f[dataset]
        except:
            chosenListBox.delete(0,END)

def add_dsetButton_OnClick(event):
    """
    Add chosen dataset to ChosenList
    """
    try:
        selected_item = treeview.selection()
        items=chosenListBox.get(0,END)
        parent_path = treeview.set(treeview.parent(selected_item), 'fullpath')
        gr_qm_pos = [i for i, j in enumerate(parent_path)if j == '"']
        group_path = parent_path[gr_qm_pos[0]+1:gr_qm_pos[1]]
        item_path = treeview.set(selected_item, 'fullpath')
        ds_qm_pos = [i for i, j in enumerate(item_path)if j == '"']
        item_name = item_path[ds_qm_pos[0]+1:ds_qm_pos[1]]
        item_fullpath = group_path+'/'+item_name
        files_list = get_current_filesName()

        if treeview.set(selected_item, "type") == 'Dataset':
            if not items:
                chosenListBox.insert(END, item_fullpath)
            elif not item_fullpath in items:
                f=h5py.File(files_list[0], 'r')
                dset_shape = f[items[0]].shape[0]
                new_dset_shape = f[item_fullpath].shape[0]
                if dset_shape == new_dset_shape:
                    chosenListBox.insert(END, item_fullpath)
                else:
                    tkMessageBox.showerror('Error',
    """Different datasets size. You can only add datasets with the same size.
    Your datasets have %s rows while dataset you tried to add has %s rows""" %(dset_shape, new_dset_shape))
    except IndexError: pass
    
def remove_Button_OnClick():
    """
    Remove chosen dataset from ChosenList
    """
    chosenListBox.delete(chosenListBox.curselection())

def make_camps_dict():
    """
    Create dictionary where keys are campaign number and values are
    their files   
    """
    files_list = get_current_filesName()
    camps_dict={}

    for single_file in files_list:
        f = h5py.File(single_file,'r')
        campaign = f['ANCILLARY_DATA/'].attrs['Campaign']
        if not campaign in camps_dict:
            camps_dict[campaign]=[f]
        else:
            camps_dict[campaign].append(f)

    return camps_dict

def c2n(camp):
    """
    Convert campaign sign (string) to integer (eg. '1A' -> 1, '3F' -> 11)
    """
    camp_dict={'1A':1, '2B':2, '2A':3, '2B':4, '2C':5, '3A':6, '3B':7,
              '3C':8, '3D':9, '3E':10, '3F':11, '3G':12, '3H':13,
              '3I':14, '3J':15, '3K':16, '2D':17, '2E':18, '2F':19, 0:0}
    return camp_dict[camp]


def extract_dsets(f, d, atrs):
    """
    Extract datasets from file
    """
    i=1000
    for atr in atrs:
        i+=1
        if len(f[atr][0:1].shape)==1:
            d[str(i)+atr] = f[atr][...].T
        else:
            #spliting multiple columns parameters to many one-column
            for n in range(0,f[atr].shape[-1]):
                d[str(i)+atr+str(n)] = f[atr][..., n]    

    atrs_to_stack =(d[x] for x in sorted(d.keys()))
    whole = np.column_stack(atrs_to_stack)
    return whole, d

def to_file_header(i2, d, fullpth):
    """
    Creates header in ascii file with datasets names
    """
    if i2==1:
        atrs_to_write = ''
        for atr2w in sorted(d.keys()):
            if len(atrs_to_write)==0:
                atrs_to_write += atr2w.split('/')[-1]
            else: atrs_to_write += ' '+atr2w.split('/')[-1]

    file_= open(fullpth, 'w')
    file_.write('camp '+atrs_to_write+'\n')
    file_.close()

def boundry_mask(f, whole):
    """
    Masks rows in GLAH data
    """
    item = chosenListBox.get(0,END)[0]
    dset_shape = f[item].shape[0]

    freqs = ['Data_40HZ','Data_1HZ','Data_4s','Data_5HZ']
    for fr in freqs:
        try:
            if f[fr+'/Geolocation/d_lat']:
                if f[fr+'/Geolocation/d_lat'][...].shape[0] == dset_shape:
                    freq = fr
                    break
        except:
            continue

    N = deg_conversion(NdegSpinBox, NminSpinBox, NsecSpinBox)
    S = deg_conversion(SdegSpinBox, SminSpinBox, SsecSpinBox)
    W = deg_conversion(WdegSpinBox, WminSpinBox, WsecSpinBox)
    E = deg_conversion(EdegSpinBox, EminSpinBox, EsecSpinBox)
    
    m1=f[freq+'/Geolocation/d_lat'][...].T
    m2=f[freq+'/Geolocation/d_lon'][...].T
    mask = np.logical_and(np.logical_and(m1 < N, m1 > S)==True, np.logical_and(m2 < E, m2 > W)==True)
    new_whole = whole[mask,:]
    
    return new_whole

def deg_conversion(Spin_deg, Spin_min, Spin_sec):
    """
    Conversion from "deg|min|sec" to "deg.XXXXXX"
    """
    try:
        deg = float(Spin_deg.get())
        min_= float(Spin_min.get())
        sec = float(Spin_sec.get())
        if deg<0:
            res = deg-(min_/60)-(sec/360)
        else: res = deg+(min_/60)+(sec/360)
        return res

    except ValueError:
        tkMessageBox.showerror(title='Error...', message='Please put correct numbers in Boundry box!')

def convertButton_OnClick():
    """
    Main chain to convert hdfs to ASCII
    """
    if not chosenListBox.get(0,END):
        tkMessageBox.showerror('Error', 'Please chose at least 1 dataset')
        return
                        
    mdir = tkFileDialog.askdirectory()
    atrs = chosenListBox.get(0,END)
    hdfs = get_current_filesName()
    i2=0
    d={}

    camps_dict = make_camps_dict()
    for campaign in sorted(camps_dict.keys()):
        i2=0
        fullpth = mdir+'/'+'conv_HDFs_%s.txt' %(campaign)
        for hdf in camps_dict[campaign]:
            start=time.time()
            f=h5py.File(hdf.filename, 'r')
            try:
                k = c2n(f['ANCILLARY_DATA/'].attrs['Campaign'])
            except KeyError: k=0
            i2+=1 #its used to write header just ones
    
            whole, d2 = extract_dsets(f, d, atrs)      

            if i2==1:
                atrs_to_write = to_file_header(i2, d2, fullpth)
                
            try:
                new_whole = boundry_mask(f, whole)
            except UnboundLocalError:
                return
            
            rows = int(new_whole.shape[0])
            camp=np.empty([rows,1])
            camp.fill(k)


            file_= open(fullpth, 'a')
            np.savetxt(file_, np.column_stack((camp,new_whole)))
            file_.close()

            end = time.time()
            res_time = end-start
            print '%s    finished in %.2f seconds' % (hdf, res_time)

    print '\nDone!'


"""
=======================GUI=======================
"""

app = Tk()
app.title('icesat_GLAH_extract')
app.geometry('580x610+200+20')


# Buttons
remove_Button = Button(app,text='Remove', borderwidth=2, font=my_FONT, command=remove_Button_OnClick)
remove_Button.place(x=480,y=355)

# Treeview
treeview = ttk.Treeview(columns=("fullpath", "type"), displaycolumns='')
scroll0 = Scrollbar(app, command=treeview.yview)
treeview.config(yscrollcommand=scroll0.set)
treeview.place(x=30,y=20, width=200, height=380)
scroll0.place(x=10,y=20,height=380)
treeview.bind('<Double-Button-1>',add_dsetButton_OnClick)

# Labels
label_chosen = Label(app, text='Chosen datasets', borderwidth=2, font=my_FONT).place(x=370,y=360)
label_N = Label(app, text='Up', borderwidth=2, font=my_FONT)
label_N.place(x=200,y=450)
label_S = Label(app, text='Down', borderwidth=2, font=my_FONT)
label_S.place(x=200,y=540)
label_E = Label(app, text='Right', borderwidth=2, font=my_FONT)
label_E.place(x=275,y=495)
label_W = Label(app, text='Left', borderwidth=2, font=my_FONT)
label_W.place(x=125,y=495)


# ListBox & Scrolls
filesListBox = Listbox(app, width=40, height=8, font=my_FONT)
scroll1 = Scrollbar(app, command=filesListBox.yview)
filesListBox.config(yscrollcommand=scroll1.set)
filesListBox.place(x=260,y=20, height=125, width=285)
scroll1.place(x=242,y=20,height=125)

chosenListBox = Listbox(app, width=40, height=10, font=my_FONT)
scroll4 = Scrollbar(app, command=chosenListBox.yview)
chosenListBox.config(yscrollcommand=scroll4.set)
chosenListBox.place(x=260,y=180, height=165, width=285)
scroll4.place(x=242, y=180, heigh=165)


# SpinBoxs
NdegSpinBox = Spinbox(app, from_=-90, to=90, width=3, font=my_FONT)
NdegSpinBox.place(x=230,y=450)
NminSpinBox = Spinbox(app, from_=0, to=60, width=2, font=my_FONT)
NminSpinBox.place(x=270,y=450)
NsecSpinBox = Spinbox(app, from_=0, to=60, width=2, font=my_FONT)
NsecSpinBox.place(x=305,y=450)

SdegSpinBox = Spinbox(app, from_=-90, to=90, width=3, font=my_FONT)
SdegSpinBox.place(x=230,y=540)
SminSpinBox = Spinbox(app, from_=0, to=60, width=2, font=my_FONT)
SminSpinBox.place(x=270,y=540)
SsecSpinBox = Spinbox(app, from_=0, to=60, width=2, font=my_FONT)
SsecSpinBox.place(x=305,y=540)

EdegSpinBox = Spinbox(app, from_=-180, to=180, width=4, font=my_FONT)
EdegSpinBox.place(x=310,y=495)
EminSpinBox = Spinbox(app, from_=0, to=60, width=2, font=my_FONT)
EminSpinBox.place(x=340,y=495)
EsecSpinBox = Spinbox(app, from_=0, to=60, width=2, font=my_FONT)
EsecSpinBox.place(x=370,y=495)

WdegSpinBox = Spinbox(app, from_=-180, to=180, width=4, font=my_FONT)
WdegSpinBox.place(x=150,y=495)
WminSpinBox = Spinbox(app, from_=0, to=60, width=2, font=my_FONT)
WminSpinBox.place(x=180,y=495)
WsecSpinBox = Spinbox(app, from_=0, to=60, width=2, font=my_FONT)
WsecSpinBox.place(x=210,y=495)

#Images
D = PhotoImage(file='dataset_icon2.gif')
G = PhotoImage(file='folder_closed_16x16.gif')

#Menu
menubar = Menu(app)
menu_open=Menu(menubar, tearoff=0)
menu_open.add_command(label='Open file(s)', command=openfilesButton_OnClick)
menu_open.add_command(label='Open directory', command=opendirButton_OnClick)
menubar.add_cascade(label='File',menu=menu_open)

menu_conv=Menu(menubar, tearoff=0)
menu_conv.add_command(label='to ASCII', command=convertButton_OnClick)
menubar.add_cascade(label='Convert',menu=menu_conv)

app.config(menu=menubar)

app.mainloop()
