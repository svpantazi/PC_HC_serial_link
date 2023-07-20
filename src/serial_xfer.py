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

import serial
# import os,sys
# import time
import threading

DEFAULT_BAUD_RATE=9600

#all this data is needed by the thread
com_port=None
baud_rate=DEFAULT_BAUD_RATE
ser_port=None
header=None
bin_file=None
bin_data=None
serial_thread=None
ts_transfer_end_callback=None
com_port_exception=None


def make_microdrive_header(data_type,block_len,start_addr,prog_len,line_num):
    header=bytearray([data_type,block_len[0],block_len[1],start_addr[0],start_addr[1],prog_len[0],prog_len[1],line_num[0],line_num[1]])
    print(header)    
    return header

def binary_file_serial_upload(sp,bin_file_name, file_header=None, binary_data=None):   
    sp.dtr=True
    sp.rts=True
    h=file_header
    if h==None:
        #read header from file
        with open(bin_file_name+'.binh', "rb") as bin_file_header:
            h=bytearray(bin_file_header.read())
            bin_file_header.close()

    print('header from file: type: {0}, len:{1}, saddr:{2}, plen:{3}, line:{4}'.format(h[0],h[1]+h[2]*256,h[3]+h[4]*256,h[5]+h[6]*256,h[7]+h[8]*256))                
    print('written header from file: ',list(h))
    written_count=sp.write(h)
    print(f'written {written_count} header bytes to serial port')

    write_buff=binary_data
    if write_buff==None:
        with open(bin_file_name, "rb") as bin_file:
            write_buff=bytearray(bin_file.read())
            bin_file.close()        
    #print(len(write_buff),' bytes of data uploaded: ',list(write_buff))            
    written_count=sp.write(write_buff)
    print(f'written {written_count} data bytes to serial port')        


def serial_binary_xfer_loop():
    global ser_port
    try:    
        if ser_port:
            print('Serial binary transferring \n')
            print('Header: ',header)
            print('File: ',bin_file)
            binary_file_serial_upload(ser_port,bin_file,file_header=header,binary_data=bin_data)

    finally:            
        if ser_port:
            ser_port.dtr=False
            ser_port.rts=False
            print('closing serial port')
            #if ser_port.out_waiting>0: 
            ser_port.reset_output_buffer()
            ser_port.cancel_write()       
            #if ser_port.in_waiting>0:
            ser_port.reset_input_buffer()
            ser_port.cancel_read()       
            ser_port.close()    #there is an internal check on is_open so no error if already closed
            print('serial port closed')
            ser_port=None                             
            if ts_transfer_end_callback: ts_transfer_end_callback()

def start_serial_xfer(on_transfer_started=None):    
    global serial_thread
    global ser_port
    global com_port_exception
    global stopping
    stopping=False
    try:
        ser_port = serial.Serial(com_port,baudrate=baud_rate, rtscts=True, dsrdtr=False)    
        print('opened serial port ',ser_port.name, ' at ',baud_rate,' baud')                     
        #if ser_port.out_waiting>0: 
        ser_port.reset_output_buffer()
        #if ser_port.in_waiting>0:
        ser_port.reset_input_buffer()
        #ser_port.set_output_flow_control(enable=True)
        ser_port.dtr=False
        ser_port.rts=False
        print(f'DTR {ser_port.dtr} RTS {ser_port.cts}')       
            
        #creating thread
        serial_thread = threading.Thread(target=serial_binary_xfer_loop) #use args to pass data to thread    
        serial_thread.start()         
        if on_transfer_started:  on_transfer_started()
    except Exception as e:
        com_port_exception=e
        if on_transfer_started:  on_transfer_started()


def stop_serial_xfer():
    global stopping
    stopping=True
    if ser_port:    
        ser_port.reset_output_buffer()        
        ser_port.cancel_write()               
        ser_port.reset_input_buffer()            
        ser_port.cancel_read()       
        #closing it here will create an exception in the transfer but that can be handled separately
        #serial_thread.join() - does not work well    

