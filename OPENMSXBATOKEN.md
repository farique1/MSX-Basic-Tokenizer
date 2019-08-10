# openMSX Basic (de)Tokenizer  

Uses **openMSX** to convert a basic program from ASCII to tokenized or vice-versa.  

It calls **openMSX** headless (without screen) and with throttle, mount a path (current = default) as a disk, load a basic file from this path, saves it with the chosen format and closes **openMSX**.  
> Be careful with the folder used as a disk. openMSX respects the MSX disk limitations of size (size of all the files must not be greater than the emulated disk size) and file name sizes.  
> Always work on copies.  

### How to use  

On the Python code itself enter the location of your **openMSX** instalation.  
Also optionally choose a machine and a extension.  
If no machine is specified the default one will be used.  
You can name a disk drive extension for machines without one. It will be plugged on the slot A by default but you can force it to slot B by writing `:SlotB` after its name.  
```
openmsx_filepath = '/<path_to>/openmsx/openmsx.app'
machine_name = 'Sharp_HB-8000_1.2'
disk_ext_name = 'Microsol_Disk:SlotB'
```
> Leave the machine and extension variables blank (`''`)  to use the **openMSX** defaults.  

From the terminal call `openmsxbatoken.py`:  
`openmsxbatoken.py <source> [destination] [-asc] [-vb]`  

`source` is the file to convert.  
If a path (absolute) is given, this path will be used to mount the disk on the MSX.  
If only a name is given the current path will be mounted as a disk on the MSX.  

`destination` is the file to be saved.  
If a path is given it will be ignored.  
If no name is given the `source` name will be used witn a `.bas` or `.asc` extension accordingly. (beware that the source CAN be overwritten).  

`-asc` save the file in ASCII instead of tokenized.  
The default save extension will be changed to `.asc`.  

`-vb` displays the openMSX output.  

### Known bugs  

An `autoexec.bas` on the disk will run automatically and possibly prevent the conversion.  
There is a problem passing file names with some special characters, "&" for instance.  

----------------------
> Made in a hurry with Python 2.7  
> Beware a little.  
