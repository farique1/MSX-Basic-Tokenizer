"""
openMSX Basic (de)Tokenizer
v1.2
Uses openMSX to tokenize ASCII MSX Basic or vice-versa.

Copyright (C) 2019-2020 - Fred Rique (farique)
https://github.com/farique1/MSX-Basic-Tokenizer

See also:
MSX Sublime Tools at
https://github.com/farique1/MSX-Sublime-Tools
Syntax Highlight, Theme, Build System, Comment Preference and Auto Completion.

MSX Basic Dignified at
https://github.com/farique1/msx-basic-dignified
Convert modern MSX Basic Dignified to traditional MSX Basic format.

openmsxbatoken.py <source> <destination> [args...]
openmsxbatoken.py -h for help.

New: 26-1-2020 v1.1
    Significant code rewrite to bring it to the Badig standard.
    Fully integrated with the Badig ecosystem.
        Can be automatically called by the build system on MSX Sublime Tools and from MSX Basic Dignified.
    Created an .ini file with file_load, file_save, machine_name, disk_ext_name, output_format, delete_original, verbose_level, openmsx_filepath.
    Verbose level and log output created to follow the Badig standard.
    Added -do (delete original) argument to delete the original file after the conversion.
    Added -of (output file) to indicate the format to save: tokenized or ASCII.
    Added -fb (from build)
    Removed -asc (replaced by -of)
    Warning if a path is issued to the destination file. The path will be removed, the destination is always saved on the same folder (the mounted MSX disk) as the source.
    Throw an error if destination is the same as the source
    Will replace spaces on file names with an _ to conform to the MSX disk specification.
    Better error handling.
"""

# for i in *.bas; do python openmsxbatoken.py "$i" -asc; done
# *** CAUTION *** An autoexec.bas on the mounted folder will crash the script

import os.path
import argparse
import subprocess
import ConfigParser
from os import remove as osremove

file_load = ''              # Source file
file_save = ''              # Destination file
machine_name = ''           # openMSX machine to open, eg: 'Sharp_HB-8000_1.2' 'Sharp_HB-8000_1.2_Disk' 'Philips_NMS_8250'
disk_ext_name = ''          # openMSX extension to open, eg: 'Microsol_Disk:SlotB'
show_output = True          # Show the openMSX stderr output
output_format = 't'         # Tokenized or ASCII output: t-tokenized a-ASCII
delete_original = False     # Delete the original file
verbose_level = 3           # Show processing status: 0-silent 1-+erros 2-+warnings 3-+steps 4-+details
is_from_build = False       # Tell if it is being called from a build system (show file name on error messages and other stuff)
openmsx_filepath = ''       # Path to openMSX ('' = local path)


def show_log(line, text, level, **kwargs):
    bullets = ['', '*** ', '  * ', '--- ', '  - ', '    ']

    try:
        bullet = kwargs['bullet']
    except KeyError:
        bullet = level

    display_file_name = ''
    if is_from_build and (bullet == 1 or bullet == 2):
        display_file_name = os.path.basename(file_load) + ': '

    line_number = line

    if verbose_level >= level:
        print bullets[bullet] + display_file_name + line_number + text
        # print bullets[bullet] + text

    if bullet == 1:
        if proc:
            proc.stdin.write('<command>type_via_keybuf poke-2,0\\r</command>')
        if is_from_build:
            print '    Tokenizing_aborted'
        else:
            print '    Execution_stoped'
            print
        raise SystemExit(0)


local_path = os.path.split(os.path.abspath(__file__))[0] + '/'
if os.path.isfile(local_path + 'openMSXBatoken.ini'):
    config = ConfigParser.ConfigParser()
    config.sections()
    try:
        config.read(local_path + 'openMSXBatoken.ini')
        file_load = config.get('DEFAULT', 'file_load') if config.get('DEFAULT', 'file_load') else file_load
        file_save = config.get('DEFAULT', 'file_save') if config.get('DEFAULT', 'file_save') else file_save
        machine_name = config.get('DEFAULT', 'machine_name') if config.get('DEFAULT', 'machine_name') else machine_name
        disk_ext_name = config.get('DEFAULT', 'disk_ext_name') if config.get('DEFAULT', 'disk_ext_name').strip() else disk_ext_name
        output_format = config.get('DEFAULT', 'Output_format') if config.get('DEFAULT', 'Output_format') else output_format
        delete_original = config.getboolean('DEFAULT', 'delete_original') if config.get('DEFAULT', 'delete_original') else delete_original
        verbose_level = config.getint('DEFAULT', 'verbose_level') if config.get('DEFAULT', 'verbose_level') else verbose_level
        openmsx_filepath = config.get('DEFAULT', 'openmsx_filepath') if config.get('DEFAULT', 'openmsx_filepath') else openmsx_filepath
    except (ValueError, ConfigParser.NoOptionError) as e:
        show_log('', 'openMSXBatoken.ini: ' + str(e), 1)

parser = argparse.ArgumentParser(description='Use openMSX to convert between ASCII and tokenized MSX Basic.')
parser.add_argument("file_load", nargs='?', default=file_load, help='The file to be converted.')
parser.add_argument("file_save", nargs='?', default=file_save, help='The file to convert to.')
parser.add_argument("-of", default=output_format, choices=['t', 'T', 'a', 'A'], help="Tokenized or ASCII output: t-tokenized(def) a-ASCII")
parser.add_argument("-do", default=delete_original, action='store_true', help="Delete original file after conversion")
parser.add_argument("-vb", default=verbose_level, type=int, help="Verbosity level: 0 silent, 1 errors, 2 +warnings, 3 +steps(def), 4 +detalis")
parser.add_argument("-fb", default=is_from_build, action='store_true', help="Tell it is running from a build system")
args = parser.parse_args()

file_load = args.file_load
file_save = args.file_save
output_format = args.of.upper()
delete_original = args.do
verbose_level = args.vb
is_from_build = args.fb

show_log('', '', 3, bullet=0)

file_load_full = file_load
file_name = os.path.basename(file_save)
save_rest = file_save.replace(file_name, '')
file_save = file_name
save_extension = '.bas'
save_argument = ''
using_machine = 'default machine'
disk_ext_slot = 'ext'
proc = ''
if openmsx_filepath == '':
    openmsx_filepath = local_path + 'openMSX.app'
if machine_name != '':
    using_machine = machine_name
    machine_name = '-machine ' + machine_name
disk_ext = disk_ext_name.split(':')
disk_ext_name = disk_ext[0].strip()
if len(disk_ext) > 1:
    disk_ext_slot = 'extb' if disk_ext[1].lower().strip() == 'slotb' else disk_ext_slot
if file_load:
    if not os.path.isfile(file_load):
        show_log('', ' '.join(['source_not_found', file_load]), 1)  # Exit
else:
    show_log('', 'source_not_given', 1)  # Exit
if output_format == 'A':
    save_extension = '.asc'
    save_argument = '",a'
if file_save == '':
    file_save = os.path.basename(file_load)
    file_save = os.path.splitext(file_save)[0][0:8] + save_extension
disk_path = os.path.dirname(file_load)
disk_path = local_path if disk_path == '' else disk_path
file_load = os.path.basename(file_load)

disk_path = disk_path.replace(' ', r'\ ')
file_load = file_load.replace(' ', '_')
file_save = file_save.replace(' ', '_')

if save_rest:
    show_log('', ' '.join(['destination_path_removed', save_rest]), 2)

if file_save == file_load:
    show_log('', ' '.join(['destination_same_as_source', file_save]), 1)  # Exit


def output(show_output, step):
    if show_output:
        # proc.stdin.flush()
        log_out = proc.stdout.readline().rstrip()
        log_out = log_out.replace('&quot;', '"')
        if '"nok"' in log_out or ' error: ' in log_out:
            log_out = log_out.replace('<reply result="nok">', '')
            proc.stdin.write('<command>quit</command>')
            show_log('', ''.join([step]), 3)
            show_log('', ''.join([log_out]), 1)  # Exit
        elif '<log level="warning">' in log_out:
            log_warning = log_out.replace('<log level="warning">', '')
            log_warning = log_warning.replace('</log>', '')
            log_out = log_out.split('<log')[0]
            log_comma = '' if log_out == '' else ': '
            show_log('', ''.join([step, log_comma, log_out]), 3)
            show_log('', ''.join([log_warning]), 2)
        else:
            log_out = log_out.replace('<openmsx-output>', '')
            log_out = log_out.replace('</openmsx-output>', '')
            log_out = log_out.replace('<reply result="ok">', '')
            log_out = log_out.replace('</reply>', '')
            log_comma = '' if log_out == '' else ': '
            show_log('', ''.join([step, log_comma, log_out]), 3)


cmd = (openmsx_filepath + '/contents/macos/openmsx ' + machine_name + ' -control stdio')
proc = subprocess.Popen([cmd], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

output(show_output, 'openMSX initialized as ' + using_machine)

# proc.stdin.write('<command>set renderer SDL</command>')
# output(show_output, 'Show screen')

proc.stdin.write('<command>set throttle off</command>')
output(show_output, 'Set throttle off')

proc.stdin.write('<command>debug set_watchpoint write_mem 0xfffe {[debug read "memory" 0xfffe] == 0} {quit}</command>')
output(show_output, 'Set quit watchpoint')

if disk_ext_name != '':
    proc.stdin.write('<command>' + disk_ext_slot + ' ' + disk_ext_name + '</command>')
    output(show_output, 'Insert disk drive extension: ' + disk_ext_name + ' at ' + disk_ext_slot)

proc.stdin.write('<command>diska insert ' + disk_path + '</command>')
output(show_output, 'insert folder as disk: ' + disk_path)

proc.stdin.write('<command>set power on</command>')
output(show_output, 'Power on')

proc.stdin.write('<command>type_via_keybuf \\r\\r</command>')  # Disk ROM ask for date, enter twice to skip
output(show_output, 'Press return twice')

proc.stdin.write('<command>type_via_keybuf load"' + file_load + '\\r</command>')
output(show_output, 'type load"' + file_load + '"')

proc.stdin.write('<command>type_via_keybuf save"' + file_save + save_argument + '\\r</command>')
output(show_output, 'type save"' + file_save + save_argument + '"')

proc.stdin.write('<command>type_via_keybuf poke-2,0\\r</command>')
output(show_output, 'Quit')

proc.wait()

file_save_full = disk_path + '/' + file_save
if os.path.isfile(file_save_full) and delete_original:
    show_log('', 'Deleting source', 3)
    show_log('', ' '.join(['delete_file:', file_load_full]), 4)
    osremove(file_load_full)

show_log('', '', 3, bullet=0)
