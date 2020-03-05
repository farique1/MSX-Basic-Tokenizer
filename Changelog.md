# MSX Basic Tokenizer  
  
## **v1.3**  
***14-2-2020***  
- Python 3.8.  
- No more forcing an 8 character file name.  
- Changed `-fb` to `-frb`.  
- Warning issued if didn't delete original.  
  
## **v1.2**  
***29-1-2020***  
- Bring version up to 1.2 to sync with **openMSX Basic (de)Tokenizer**.  
- Fully integrated with the **Badig**  ecosystem.  
	- Can be automatically called by the build system on **MSX Sublime Tools** and from **MSX Basic Dignified**.  
- Created an `.ini` file with `file_load`, `file_save`, `export_list`, `delete_original` and `verbose_level`.  
- Verbose level and log output upgraded to follow the **Badig** standard and elevated the tokenisation step by step to level 5.  
- Added `-do` *(delete original)* argument to delete the original ASCII file after the conversion.  
- Removed the `-bw` *(byte width)* argument.  
- Changed `-sl` *(save list)* to `-el` *(export list)* to avoid clash with **Dignified**'s `-sl` *(show labels)*.  
- `-el` now takes the numeric arguments from `-bw`.  
- Better `-fb` *(from build)* response  
- Throw an error if `destination` is the same as the `source`  
- Removed unnecessary global variables from functions.  
- Better error handling  
- Small code optimizations  
  
## **v1.0**  
***17-9-2019***  
- .mlt Assembler like List file export option  
	- The .mtl file uses the same MSX Sublime Tools syntax highlight as the MSX Basic  
- Fixed the order of the instructions on the token conversion list  
	- If a smaller had the same chars of the start of a larger one it would be picked first. Larger should come first  
- Fixed all numbers parsing and conversions  
	- Fixed rounding of double precision number  
	- Added scientific notation  
- Fixed bug with empty commas on ON GOTO/GOSUB  
- Fixed discrepancy on numbers after AS on OPEN without the preceding #  
- Small code optimization  
  
## **v0.1**  
- Initial release.  
  
---  
  
# openMSX Basic (de)Tokenizer  
  
## **v1.3**  
***14-2-2020***  
  
- Python 3.8.  
- Better subprocess call and IO handling.  
- Improved verbose output.  
- Changed `-fb` to `-frb`.  
- Warning issued if didn' delete original.  
- Fixed bug and better handling when trying to load or save files with spaces and more than 8 characters.  
	- Files opened on openMSX now are internally cropped to 8 char and have spaces replaced with `_`  
	- Error if conflicting file names due to disk format limitations.  
  
## **v1.2**  
***29-1-2020***  
- Significant code rewrite to bring it to the **Badig** standard.  
- Fully integrated with the **Badig**  ecosystem.  
	- Can be automatically called by the build system on **MSX Sublime Tools** and from **MSX Basic Dignified**.  
- Created an `.ini` file with `file_load`, `file_save`, `machine_name`, `disk_ext_name`, `output_format`, `delete_original`, `verbose_level`, `openmsx_filepath`.  
- Verbose level and log output created to follow the **Badig** standard.  
- Added `-do` *(delete original)* argument to delete the original file after the conversion.  
- Added `-of` *(output file)* to indicate the format to save: tokenized or ASCII.  
- Added `-fb` *(from build)*  
- Removed `-asc` (replaced by `-of`)  
- Warning if a path is issued to the `destination` file. The path will be removed, the `destination` is always saved on the same folder (the mounted MSX disk) as the `source`.  
- Throw an error if `destination` is the same as the `source`  
- Will replace spaces on file names with an `_` to conform to the MSX disk specification.  
- Better error handling.  
  
## **v1.1**  
***9-8-2019***  
- No more savestates. Emulator now boots with chosen (or default) machine and, if necesssary, disk extension.  
- Extension can be at slot A or B. Default A, add `:SlotB` after the name for slot B  
- Log output moved to function with more info  
- Better error handling  
  
## **v1.0**  
- Initial release.  
