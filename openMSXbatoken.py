"""
openMSX Basic (de)Tokenizer
v1.1

Uses openMSX to convert an MSX basic program from ASCII to tokenized or vice-versa.

Copyright (C) 2019 - Fred Rique (farique)
https://github.com/farique1/MSX-Basic-Tokenizer/

9-8-2019
NEW:
No more savestates, emulator boots and with chosen (or default) machine and load disk extension if necesssary
Extension can be at slot A or B. Default A, add :SlotB after the name for slot B
Log output moved to function with more info
Better error handling
NOTE:
autoexec.bas on the disk will run automatically and possibly prevent the conversion
problem passing special characters on the file names. "&" for instance
"""

# for i in *.bas; do python openmsxbatoken.py "$i" -asc; done
# *** CAUTION *** An autoexec.bas will crash the script

import subprocess
import argparse
import os.path

openmsx_filepath = '/Users/Farique/desktop/pessoal/retro/openmsx/openmsx.app'
machine_name = ''  # 'Sharp_HB-8000_1.2' 'Sharp_HB-8000_1.2_Disk' 'Philips_NMS_8250'
disk_ext_name = ''  # 'Microsol_Disk:SlotB'

local_path = os.path.abspath(__file__)
local_path = os.path.split(local_path)[0]

file_load = ''
file_save = ''
show_output = False
save_ascii = False
save_extension = '.bas'
save_argument = ''
using_machine = 'default machine'
disk_ext_slot = 'ext'

parser = argparse.ArgumentParser(description='Use openMSX to convert between ASCII and tokenized MSX Basic.')
parser.add_argument("file_load", nargs='?', default=file_load, help='The file to be converted.')
parser.add_argument("file_save", nargs='?', default=file_save, help='The file to convert to.')
parser.add_argument("-asc", action='store_true', default=save_ascii, help='Save the file in ASCII mode.')
parser.add_argument("-vb", action='store_true', default=show_output, help='Verbose mode. Show the output from openMSX.')
args = parser.parse_args()

file_load = args.file_load
file_save = args.file_save
show_output = args.vb
save_ascii = args.asc

if machine_name != '':
    using_machine = machine_name
    machine_name = '-machine ' + machine_name

disk_ext = disk_ext_name.split(':')
disk_ext_name = disk_ext[0].strip()
if len(disk_ext) > 1:
    disk_ext_slot = 'extb' if disk_ext[1].lower().strip() == 'slotb' else disk_ext_slot

if not file_load:
    print 'Source not given'
    raise SystemExit(0)

if save_ascii:
    save_extension = '.asc'
    save_argument = '",a'

if args.file_save == '':
    file_save = os.path.basename(file_load)
    file_save = os.path.splitext(file_save)[0][0:8] + save_extension

disk_path = os.path.dirname(file_load)
disk_path = local_path if disk_path == '' else disk_path
file_load = os.path.basename(file_load)


def output(show_output, step):
    # proc.stdin.flush()
    log_out = proc.stdout.readline().rstrip()
    if '"nok"' in log_out or ' error: ' in log_out:
        proc.stdin.write('<command>quit</command>')
        print log_out + ': ' + step
        print 'Execution stopped'
        raise SystemExit(0)
    else:
        if show_output:
            print log_out + ': ' + step


file_save = os.path.basename(file_save)
file_save = os.path.splitext(file_save)[0][0:8] + os.path.splitext(file_save)[1]

disk_path = disk_path.replace(' ', r'\ ')
file_load = file_load.replace(' ', r'\ ')
file_save = file_save.replace(' ', r'\ ')


cmd = (openmsx_filepath + '/contents/macos/openmsx ' + machine_name + ' -control stdio')
proc = subprocess.Popen([cmd], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

output(show_output, 'Initialized as ' + using_machine)

# proc.stdin.write('<command>set renderer SDL</command>')
# output(show_output, 'Show screen')

proc.stdin.write('<command>set throttle off</command>')
output(show_output, 'Turn throttle on')

proc.stdin.write('<command>debug set_watchpoint write_mem 0xfffe {[debug read "memory" 0xfffe] == 0} {quit}</command>')
output(show_output, 'Set quit watchpoint')

if disk_ext_name != '':
    proc.stdin.write('<command>' + disk_ext_slot + ' ' + disk_ext_name + '</command>')
    output(show_output, 'Insert disk drive extension: ' + disk_ext_name + ' at ' + disk_ext_slot)

proc.stdin.write('<command>diska insert ' + disk_path + '</command>')
output(show_output, 'insert folder as disk: ' + disk_path)

proc.stdin.write('<command>set power on</command>')
output(show_output, 'Power on')

proc.stdin.write('<command>type_via_keybuf \\r\\r</command>')  # Disk ROM ask for date
output(show_output, 'Press return twice')

proc.stdin.write('<command>type_via_keybuf load"' + file_load + '\\r</command>')
output(show_output, 'type load"' + file_load)

proc.stdin.write('<command>type_via_keybuf save"' + file_save + save_argument + '\\r</command>')
output(show_output, 'type save"' + file_save + save_argument)

proc.stdin.write('<command>type_via_keybuf poke-2,0\\r</command>')
output(show_output, 'Quit')
