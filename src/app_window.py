'''
    Copyright (C) 2023 Stefan V. Pantazi (svpantazi@gmail.com)    
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see http://www.gnu.org/licenses/.
'''

import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext 
from ui_elements import ChoiceEntry, HexEntry

from zx_screen_consts import SCREEN_DATA_SIZE
from zx_screen_mem import plot_mem_scr_data

from tzxlib.tzxfile import TzxFile
from tzxlib.tapfile import TapHeader, TapData

import serial
from serial.tools.list_ports import comports
import serial_xfer as SX

APP_TITLE="PC-HC serial xFer v0.1 (S.V.P., Jul 2023)"
DEFAULT_FONT= ("Arial", 11)
INFO_LABEL_TEXT_LOAD_BINARY='Command for serial transfer:   LOAD *"b" '
INFO_LABEL_TEXT_LOAD_BINARY_SCREEN='Command for serial transfer:   LOAD *"b" SCREEN$'       
                
class MainWin(tk.Tk):
    def __init__(self, *args, **kwargs):        
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.geometry('512x615+300+100')
        self.title(APP_TITLE)
        self.resizable(0, 0)     #no resizing        
           
        self.protocol("WM_DELETE_WINDOW", self.close_app)                
        self.bind("<<custom-event>>",self.transfer_ended_event)
        self.setup_UI()


    def setup_UI(self):
        self.canvas=tk.Canvas(self,width=512,height=384,bg='white')        
        self.canvas.pack()

        #tab controls
        tabControl = ttk.Notebook(self)
        tabControl.pack(expand=1, fill="both")
        
        upload_tab_UI = tk.Frame(tabControl)
        upload_tab_UI.pack(side="top", fill="both", expand = True)
        tabControl.add(upload_tab_UI, text='Binary upload')
       
        self.file_list=ttk.Treeview(upload_tab_UI,show='tree')        
        self.file_list.bind("<<TreeviewSelect>>", self.select_upload_file )
        self.file_list.grid(column = 0, row = 1,rowspan=9)        
        def file_hierarchy(file,path):
            for file_name in os.listdir(path):
                full_path=os.path.join(path,file_name)                
                if os.path.isdir(full_path) or file_name[-3:].lower() in ['scr','bin','tzx']:
                    new_file=self.file_list.insert(file,'end',text=file_name,iid=full_path,open=False)
                    if os.path.isdir(full_path):
                        #recursion
                        file_hierarchy(new_file,full_path)
        file_hierarchy('',path=os.path.abspath('../'))

        self.data_type_entry=ChoiceEntry(upload_tab_UI,atitle="As binary",choices=('BASIC Program (0)','Number Array (1)','Char Array (2)','Code Block (3)'), default_idx=3, width=14, acolspan=2,arow=1,acol=1)                        
        self.block_length_entry=HexEntry(upload_tab_UI,atitle="Binary length",ahval='0x0000',arow=2,acol=1)
        self.program_length_entry=HexEntry(upload_tab_UI,atitle="Program length",ahval='0x0000',arow=3,acol=1)        
        self.address_location_entry=HexEntry(upload_tab_UI,atitle="Dest. address",ahval='0x4000',arow=4,acol=1)        
        self.auto_start_line_entry=HexEntry(upload_tab_UI,atitle="Auto start line",ahval='0xFFFF',arow=5,acol=1)        
        self.baud_rate_entry=ChoiceEntry(upload_tab_UI,atitle="Upload at",choices=('1200','2400','4800','9600','19200','38400'), default_idx=3, width=6, acolspan=1,arow=6,acol=1,asuffix='baud')                
        
        #determining com ports available on this machine
        port_list=[p.device for p in serial.tools.list_ports.comports(include_links=True)]
        
        if len(port_list)==0:
            messagebox.showinfo(APP_TITLE,"No serial port available")
            self.close_app()
        else:                     
            self.com_port_entry=ChoiceEntry(upload_tab_UI,atitle="On COM port",choices=port_list, default_idx=0, width=12, acolspan=2,arow=7,acol=1,asuffix='')                                               

        # START STOP
        self.start_stop_upload_button = ttk.Button(upload_tab_UI, text="Start", command=self.start_stop_serial_upload)
        self.start_stop_upload_button.grid(column =2, row = 8, sticky=tk.W)

        self.info_label=ttk.Label(upload_tab_UI, text=INFO_LABEL_TEXT_LOAD_BINARY)
        self.info_label.grid(column=1,row=9, columnspan=3, sticky=tk.W)

        #debug tab
        debug_tab_UI = tk.Frame(tabControl)
        debug_tab_UI.pack(side="top", fill="both", expand = True)
        debug_tab_UI.grid_rowconfigure(0, weight=1)
        debug_tab_UI.grid_columnconfigure(0, weight=1)
        tabControl.add(debug_tab_UI, text='Debug')

        self.debug_text = scrolledtext.ScrolledText(debug_tab_UI, wrap=tk.WORD)
        self.debug_text.pack(fill='both', side='left', expand=True)
        self.debug_msg('PC to HC serial ')

    def draw_screen_file(self,screen_file_name):
        with open(screen_file_name, "rb") as scr_file:
            data=bytearray(scr_file.read(SCREEN_DATA_SIZE))
            scr_file.close()
            plot_mem_scr_data(data,self.canvas)

    def select_upload_file(self,event):
        SX.bin_file=None
        SX.bin_data=None
        self.data_type_entry.set_index(3)
        self.info_label.configure(text='')
        self.block_length_entry.set('0x0000')
        self.address_location_entry.set('0xffff')
        self.auto_start_line_entry.set('0xffff')
        self.program_length_entry.set('0x0000')        
        print("selected"+str(event))
        widget = event.widget        
        print(widget.selection())
        full_path = widget.selection()[0]
        file_name=self.file_list.item(full_path,"text")
        print('You selected file "%s" located at path "%s"' % (file_name,full_path))
        file_size=os.stat(full_path).st_size
        if os.path.isfile(full_path):
            if file_name.lower().endswith('tzx'):
                #read header and blocks to determine size
                tzx =TzxFile()
                tzx.read(full_path)
                self.debug_msg('Opened TZX file:'+full_path)
                c=1
                for b in tzx.blocks:
                    self.debug_msg('%3d  %-27s %s %d' % (c, b.type, str(b),b.id))
                    c+=1
                    
                SX.bin_file=None
                SX.bin_data=None
                data_block_idx=0
                data_block_found=False
                while data_block_idx<len(tzx.blocks) and not data_block_found:
                    if (tzx.blocks[data_block_idx].id==16):
                        if isinstance(tzx.blocks[data_block_idx].tap,TapHeader):
                            #fill in header data
                            tap_header=tzx.blocks[data_block_idx].tap
                            self.data_type_entry.set_index(tap_header.typeId())                                    
                            self.info_label.configure(text='Program name: '+tap_header.name())
                            self.block_length_entry.set(hex(tap_header.length()))
                            self.address_location_entry.set('0xffff')
                            self.auto_start_line_entry.set(hex(tap_header.param1()))
                            self.program_length_entry.set(hex(tap_header.param2()))
                            data_block_idx+=1
                    if (tzx.blocks[data_block_idx].id==16):                            
                        if isinstance(tzx.blocks[data_block_idx].tap,TapData):
                            if data_block_idx==0: self.block_length_entry.set(hex(len(tzx.blocks[data_block_idx].tap.data[1:-1])))
                            SX.bin_file=self.file_list.selection()[0]
                            #needs tweaking to eliminate first and last bytes
                            SX.bin_data=tzx.blocks[data_block_idx].tap.data[1:-1]
                            data_block_found=True
                    data_block_idx+=1                     
                if not data_block_found:
                    messagebox.showinfo(APP_TITLE,"Could not find a standard speed data block in TZX file (block count {0})".format(len(tzx.blocks)))

            elif file_size==SCREEN_DATA_SIZE:
                self.draw_screen_file(full_path)            
                self.data_type_entry.set('Code Block (3)')
                self.block_length_entry.set(hex(SCREEN_DATA_SIZE))
                self.address_location_entry.set('0x4000')
                self.program_length_entry.set('0xffff')
                self.auto_start_line_entry.set('0xffff')
                self.info_label.configure(text=INFO_LABEL_TEXT_LOAD_BINARY_SCREEN)            
                SX.bin_file=self.file_list.selection()[0]
            elif file_name.lower().endswith('bin'):
                #bin binh file pair            
                if os.path.isfile(full_path+'h'):
                    with open(full_path+'h', "rb") as bin_header_file:
                        h=bytearray(bin_header_file.read())                
                        self.data_type_entry.set_index(h[0])#flag byte
                        if len(h)==17:#basic program or arrays                        
                            prog_name=h[1:11].decode()
                            self.info_label.configure(text='Program name: '+prog_name)
                            self.block_length_entry.set(hex(h[11]+h[12]*256))                        
                            self.auto_start_line_entry.set(hex(h[13]+h[14]*256))#param 1
                            self.program_length_entry.set(hex(h[15]+h[16]*256))#param 2
                            self.address_location_entry.set('0xffff')#unused
                        elif len(h)==9:#code block
                            self.info_label.configure(text=INFO_LABEL_TEXT_LOAD_BINARY)
                            self.block_length_entry.set(hex(h[1]+h[2]*256))
                            self.address_location_entry.set(hex(h[3]+h[4]*256))
                            self.program_length_entry.set(hex(h[5]+h[6]*256))                        
                            self.auto_start_line_entry.set(hex(h[7]+h[8]*256))                    
                    
                SX.bin_file=self.file_list.selection()[0]
            else:
                #arbitrary binary files, all I can do is set the size, rest is up to the user
                print('file')
                self.info_label.configure(text=INFO_LABEL_TEXT_LOAD_BINARY)            
                self.block_length_entry.set(hex(file_size))

    def start_stop_serial_upload(self):                
        if not SX.ser_port:
            SX.ts_transfer_end_callback=ts_transfer_end_callback
            SX.com_port=self.com_port_entry.get_value()
            SX.baud_rate=self.baud_rate_entry.get_value()

            #NOTE binary transfers - regardless of being programs or not are always using 9 byte headers
            SX.header=SX.make_microdrive_header(
                    self.data_type_entry.get(),
                    self.block_length_entry.get_bytes(),
                    self.address_location_entry.get_bytes(),
                    self.program_length_entry.get_bytes(),
                    self.auto_start_line_entry.get_bytes())                    
            if self.file_list.selection():
                self.start_stop_upload_button.configure(state='disabled')        

                def transfer_started():
                    if SX.ser_port:
                        self.start_stop_upload_button.configure(text='Stop', state='')
                    else:
                        self.start_stop_upload_button.configure(text='Start', state='')
                        self.debug_msg(SX.com_port_exception.args[0])
                        messagebox.showinfo(APP_TITLE,"Serial port "+SX.com_port
                            +" error \n"+SX.com_port_exception.args[0])                            
                    
                SX.start_serial_xfer(transfer_started)
        else:            
            self.start_stop_upload_button.configure(state='disabled')
            SX.stop_serial_xfer()


    def transfer_ended_event(self,evt):
        print('transfer done!',evt)
        self.debug_msg('transfer done!')        
        self.start_stop_upload_button.configure(text='Start', state='')


    def debug_msg(self,msg):
        self.debug_text.insert('end', msg+'\n')

    def close_app(self):
        if SX.ser_port:
            SX.stop_serial_xfer()
        self.quit()

app=None

def ts_transfer_end_callback():
    app.event_generate("<<custom-event>>")
        
def app_main():
    global app
    app = MainWin()    
    app.mainloop()
