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
from zx_screen_consts import *

def plot_mem_scr_data(data,canvas):    
    canvas.delete('all')#canvas calls are really taxing CPU and memory resources must delete previous objects created
    data_len=min(len(data),COLOR_BLOCK_PTR)
    for i in range(0,data_len):
            third_index=        i // THIRD_BYTE_SIZE
            third_byte_idx=     i %  THIRD_BYTE_SIZE

            char_bit_row_idx =          third_byte_idx // THIRD_SCALINES_BYTE_SIZE 
            third_scanlines_byte_idx =  third_byte_idx  % THIRD_SCALINES_BYTE_SIZE            
            third_char_row_idx =        third_scanlines_byte_idx // SCR_CHAR_WIDTH
            char_col_idx =              third_scanlines_byte_idx  % SCR_CHAR_WIDTH 

            char_row_idx=               third_index*SCR_THIRD_CHAR_HEIGHT+third_char_row_idx
            y=char_row_idx*CHAR_BIT_HEIGHT+char_bit_row_idx
            
            #figure out color if data is available
            color_addr=COLOR_BLOCK_PTR+char_row_idx*SCR_CHAR_WIDTH+char_col_idx            
            if color_addr<len(data):
                ink_color_idx=data[color_addr] & 7                
                paper_color_idx=(data[color_addr] >> 3) & 7
                bright=(data[color_addr] >> 6) & 1
            else:
                ink_color_idx=0
                paper_color_idx=7
                bright=0
            
            for xbi in range(0,8):
                if data[i] & (128 >> xbi):
                    color=PALETTE[ink_color_idx][bright]
                else: color=PALETTE[paper_color_idx][bright]
                x=char_col_idx*CHAR_BIT_WIDTH+xbi                
                
                canvas.create_rectangle(2*x, 2*(y), 2*x+1,2*(y)+1,fill=color,outline=color, state='disabled')
                


