# PC_HC_serial_link
PC to HC serial data link
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

Stefan V. Pantazi (svpantazi@gmail.com)

July 2023

BACKGROUND

This software application allows transfer of data and programs from a PC to a HC (ZX-spectrum compatible) computer equipped with a IF1 interface.
The serial communication software and hardware on the IF1 is well described in the Spectrum Microdrive book. There is variation on the actual connection of PC serial port signals so some experiments have been necessary in order to determine the exact configuration. Having the PC serial port in the RTS/CTS flow control configuration seems to work well.

For documentation on how to construct a serial cable, read the PDF file in the doc folder.
 
Currently, the application allows transferring binary data at the maximum rate of 19200 baud. Screen data transfers pose no praticular problems since screens are simple data blocks with a fixed size of 6912 bytes and a precise memory location where they need to be transferred (0x4000).

Code blocks and Basic program data on the other hand, have variable lengths and require additional metadata that is typically stored in 9 byte (microdive header) or 17 bytes (tape header).

The application is limited to the transfer of simple binary files (with or without an additional header file) or to those with at most a header and a data block that can be read from a TXZ file. Note that the TZX data blocks should be standard speed (type 16) headers or data blocks.

The application has a GUI allows selecting a file to transfer, setting the transfer parameters (length, destination address, auto start line, etc.) as well as the serial communication (port and baud rate). Selected screen files are also displayed in the application.

INSTALLATION

Clone the project folder on your machine. It contains the source code, a binary executable, documentation (this readme and and aditional PDF file) and an asset folder with examples of binary file programs, screens and tzx files that are known to work.

To run the application you need to have Python 3 installed on your machine and to launch PC_HC_serial.py in the src folder. If you get errors about missing modules, there are only two dependencies to install: tzxtools and pyserial. You can install both of them using pip: 

pip install tzxtools pyserial

If you are on Windows and prefer to run an executable binary instead, there is one available in bin folder.

REFERENCES

Spectrum Microdrive book
    https://ia801504.us.archive.org/23/items/spectrum_microdrive_book/spectrum_microdrive_book.pdf

Game art - in form of screen files to test image data transfer
    https://zxart.ee/eng/graphics/games/

Tkinter for GUI development
    https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/index.html

PySerial for serial port programming
    https://pyserial.readthedocs.io/en/latest/pyserial_api.html

tzxtools - a collection for processing tzx files
    Copyright (C) 2018 Richard "Shred" Körber
    https://github.com/shred/tzxtools    
