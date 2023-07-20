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

import tkinter as tk
from tkinter import ttk


class HexEntry(ttk.Entry):
    '''UI text entry for 16 bit hexadecimal values    '''
    def __init__(self, *args, **kwargs):
        stitle=kwargs.pop('atitle','')
        shval=kwargs.pop('ahval','0x0000')
        srow=kwargs.pop('arow',0)
        scol=kwargs.pop('acol',0)
        container=args[0]
        super().__init__(*args,**kwargs)        
        self.title_tabel=ttk.Label(container,  justify=tk.LEFT, text=stitle).grid(row=srow, column=scol, sticky=tk.E )
        self.string_var = tk.StringVar()
        self.string_var.set('0x0000')
        self.int_var = tk.IntVar()
        #setup validation
        self.configure(width=6, validate='key',validatecommand=(self.register(self.validate),'%d', '%i', '%S'),textvariable=self.string_var)        
        self.grid(row = srow, column = scol+1 , padx=4,pady=0, sticky=tk.W )        
        self.suffix_label=ttk.Label(container,  justify=tk.LEFT)
        self.suffix_label.grid(row=srow, column=scol+2, sticky=tk.W)
        self.set(shval)    
        

    def validate(self, why, where, what):
        #see https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/entry-validation.html
        print('validate hex entry  %s, %s, %s'%(why, where, what) )
        hexval=self.string_var.get()        
        if why=='0':
            hexval=hexval[:int(where)]+hexval[int(where)+len(what):]
        elif why=='1':            
            hexval=hexval[:int(where)]+what+hexval[int(where):]
        print('new string: ',hexval)
        try:
            int_val=int(hexval,base=16)                
            if (0x0000<=int_val<=0xffff):
                print('valid')
                self.int_var.set(hexval)
                self.suffix_label.configure(text='(%s)'%(str(self.int_var.get()),))                
                return True

            print('invalid')                
            return False                
        except:
            print('invalid')                
            return False                

    def set(self,hexval):
        if isinstance(hexval,str):
            try:
                int_val=int(hexval,base=16)
            except:
                int_val=0
            finally:
                self.string_var.set(hex(int_val))
                self.int_var.set(int_val)
        elif isinstance(hexval,int) and (0x0000<=hexval<=0xffff):
            self.int_var.set(hexval)
            self.string_var.set(str(hexval))
        else:
            self.set(0x0000)        
        #updates the decimal representation of the 16 bit integer value
        self.suffix_label.configure(text='(%s)'%(str(self.int_var.get()),))

    def get(self):
        return self.int_var.get()

    def get_bytes(self):
        return self.int_var.get().to_bytes(2,byteorder='little')


class ChoiceEntry(ttk.Combobox):
    '''UI entry for list of predefined choices    '''
    def __init__(self, *args, **kwargs):
        stitle=kwargs.pop('atitle','')
        schoices=kwargs.pop('choices',())
        sdefault_idx=kwargs.pop('default_idx',-1)
        srow=kwargs.pop('arow',0)
        scol=kwargs.pop('acol',0)
        scolspan=kwargs.pop('acolspan',0)
        ssuffix=kwargs.pop('asuffix','')        
        container=args[0]
        super().__init__(*args,**kwargs)        
        ttk.Label(container,  justify=tk.LEFT, text=stitle).grid(row=srow, column=scol,sticky=tk.E)    
        
        self['values'] = schoices
        self.grid(row = srow, column = scol+1,  columnspan=scolspan, padx=4,pady=0, sticky=tk.W)
        self.current(newindex=sdefault_idx)
        if ssuffix!='': ttk.Label(container,  justify=tk.LEFT, text=ssuffix).grid(row=srow, column=scol+2, padx=0,sticky=tk.W )                

    def get(self):                
        return self.current()
    
    def get_value(self):                
        return self['values'][self.current()]

    def set(self,value):
        new_idx=self['values'].index(value)
        self.current(newindex=new_idx)

    def set_index(self,idx):
        self.current(newindex=idx)
