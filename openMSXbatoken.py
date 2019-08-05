import subprocess
import argparse
import os.path

openmsx_filepath = '/<path_to>/openmsx/openmsx.app'
savestate_filepath = '/<path_to>/savestates/savestates.oms'

local_path = os.path.abspath(__file__)
local_path = os.path.split(local_path)[0]

file_load = ''
file_save = ''
show_output = False
save_ascii = False
save_extension = '.bas'
save_argument = ''

parser = argparse.ArgumentParser(description='Use openMSX to convert between ASCII and tokenized MSX Basic.')
parser.add_argument("file_load", nargs='?', default=file_load, help='The file to be converted.')
parser.add_argument("file_save", nargs='?', default=file_save, help='The file to convert to.')
parser.add_argument("-asc", action='store_true', help='Save the file in ASCII mode.')
parser.add_argument("-vb", action='store_true', help='Verbose mode. Show the output from openMSX.')
args = parser.parse_args()

file_load = args.file_load
file_save = args.file_save
show_output = args.vb
save_ascii = args.asc

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


def output(show_output):
    if show_output:
        proc.stdin.flush()
        print proc.stdout.readline().rstrip()


disk_path = disk_path.replace(' ', r'\ ')
file_load = file_load.replace(' ', r'\ ')
file_save = file_save.replace(' ', r'\ ')

cmd = (openmsx_filepath + '/contents/macos/openmsx -control stdio -savestate ' + savestate_filepath)
proc = subprocess.Popen([cmd], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

proc.stdin.write('<command>set throttle off</command>')
output(show_output)
proc.stdin.write('<command>debug set_watchpoint write_mem 0xfffe {[debug read "memory" 0xfffe] == 0} {quit}</command>')
output(show_output)
proc.stdin.write('<command>diska eject</command>')
output(show_output)
proc.stdin.write('<command>diska insert ' + disk_path + '</command>')
output(show_output)
proc.stdin.write('<command>type_via_keybuf load"' + file_load + '\\r</command>')
output(show_output)
proc.stdin.write('<command>type_via_keybuf save"' + file_save + save_argument + '\\r</command>')
output(show_output)
# proc.stdin.write('<command>set renderer SDL</command>')
proc.stdin.write('<command>type_via_keybuf poke-2,0\\r</command>')
output(show_output)
