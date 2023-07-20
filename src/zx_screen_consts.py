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

COLOR_BLOCK_PTR=6144
COLOR_BLOCK_LEN=768
CHAR_BIT_WIDTH=8
CHAR_BIT_HEIGHT=8
SCR_CHAR_WIDTH=32
SCR_THIRD_CHAR_HEIGHT=8
SCR_THIRDS=3
SCR_THIRD_BIT_HEIGHT=CHAR_BIT_HEIGHT*SCR_THIRD_CHAR_HEIGHT
SCREEN_DATA_SIZE=COLOR_BLOCK_PTR+COLOR_BLOCK_LEN
THIRD_SCALINES_BYTE_SIZE=SCR_CHAR_WIDTH*SCR_THIRD_CHAR_HEIGHT
THIRD_BYTE_SIZE=THIRD_SCALINES_BYTE_SIZE*CHAR_BIT_HEIGHT

PALETTE=[
    ["#000","#000"],#black
    ["#00c","#00f"],#blue
    ["#c00","#f00"],#red
    ["#c0c","#f0f"],#magenta
    ["#0c0","#0f0"],#green
    ["#0cc","#0ff"],#cyan    
    ["#cc0","#ff0"],#yellow
    ["#ccc","#fff"],#white
]
