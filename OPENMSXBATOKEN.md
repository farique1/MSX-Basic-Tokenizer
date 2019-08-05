# openMSX Basic (de)Tokenizer  

Uses **openMSX** to convert a basic program from ASCII to tokenized or vice-versa.  

It calls **openMSX** headless (without screen) and with throttle, mount a path (current = default) as a disk, load a basic file from this path, saves it with the chosen format and closes **openMSX**.  

For the sake of speed, an **openMSX** `savestate` file with disk drive enabled is needed.  

### How to use  

On the Python code itself enter the location of your **openMSX** instalation and the location of the `savestate` file:  
```
openmsx_filepath = '/<path to>/openmsx/openmsx.app'  
savestate_filepath = '/<path_to>/savestates/savestate.oms'  
```

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

----------------------
> Made in a hurry with Python 2.7  
> Beware a little.
