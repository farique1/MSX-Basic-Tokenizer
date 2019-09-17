# MSX Basic Tokenizer  
## **v1.0**  

***17-9-2019***   
- .mlt Assembler like List file export option  
- - The .mtl file uses the same MSX Sublime Tools syntax highlight as the MSX Basic  
- Fixed the order of the instructions on the token conversion list  
- - If a smaller had the same chars of the start of a larger one it would be picked first. Larger should come first  
- Fixed all numbers parsing and conversions  
- - Fixed rounding of double precision number  
- - Added scientific notation  
- Fixed bug with empty commas on ON GOTO/GOSUB  
- Fixed discrepancy on numbers after AS on OPEN without the preceding #  
- Small code optimization  

## **v0.1**  
- Initial release.  



# openMSX Basic (de)Tokenizer  
## **v1.1**  

***9-8-2019***  
- No more savestates. Emulator now boots with chosen (or default) machine and, if necesssary, disk extension.  
- Extension can be at slot A or B. Default A, add `:SlotB` after the name for slot B  
- Log output moved to function with more info  
- Better error handling  

## **v1.0**  
- Initial release.  
