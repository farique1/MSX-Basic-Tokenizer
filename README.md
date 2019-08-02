# MSX-Basic-Tokenizer  
v0.1  

Converts a MSX Basic ASCII program to tokenised format.  

Lightly tested with short programs and a big one only.  
There should be a lot of fringe cases and specific behaviour not found or tested yet.  

Usage:  
`msxbatoken.py <source> [destination] [-vb #] [-fb]`  

If `destination`is not given, the file will be saved as `source` with a `.bas` extension.  
(Might overwrite the source. Use `.asc` for ASCII Basic listings.)  

`-vb #`  
Verbose:  
0 - Silent  
1 - Errors  
2 - Erros + Warnings  
3 - Erros + Warnings + Steps  

`-fb`  
From Build:  
Tells MSX Basic Tokenizer it is running from a build system an adjust some log output.  


> Made with Python 2.7

-------------------------------------  

> TODO:  
> - Check the order of the instructions on the list.  
If a smaller has the same chars of the start of a larger one it will be picked first. Larger should come first  
> - Whatever else. There should be thousands of fringe cases not covered here o.O !  

> NOTE:  
> - MSX &b tokenizes anything after it as characters except when a command is reched (but not '=' for instance)  
The implementation here only looks for 0 and 1, reverting back to the normal parsing on other characters  
> - Different behaviour from MSX while encoding overflowed lines on jump instructions  
MSX seems to split the number (with 0e) in legal parts, here it throw an error  
> - Line number too high throw an error  
> - Line number out of order throw an error  
