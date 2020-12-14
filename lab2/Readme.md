# jsccf

Renaming and documenting tool for JavaScript 

# Installation

    pip install jsccf==0.8.0
    

# Commands help

    jsccf [args]
      
    Arguments:  
      -h, --help         show this help message and exit
      -p P               Fix/Verify .js project in <str:path> dir
      -d D               Fix/Verify .js files in <str:path> dir
      -f F               Fix/Verify .js file by <str:path> path
      --out-log OUT_LOG  Output log files path
      -v, --verify       Use verification <no-args>
      -fix               Fix and save result files output <no-args>

      
### Usage sample

    jsccf -f sample/test1.js -fix --out-log .
    
    
# Requirements

- python>=3.6


## Implemented
- Renaming classes
- Renaming global functions
- Renaming class methods
- Renaming constants
- Renaming variables
- Renaming files