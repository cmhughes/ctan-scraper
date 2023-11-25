# ctan-scraper.py

`ctan-scraper.py` is a `python` script to *web scrape* [https://ctan.org/](https://ctan.org/).

## version

    ctan-scraper.py, version 0.1, 2023-11-25

## author
Chris Hughes (cmhughes)

## example
Running the following command
```
ctan-scraper.py --path "macros/latex/contrib/abnt/" --output myfile1.txt ".*?\.cls"
```
gives all of the `.cls` files in the directory `<mirror>/macros/latex/contrib/abnt/`, and
you receive
```
INFO - [re.compile('macros'), re.compile('latex'), re.compile('contrib'), re.compile('abnt')]
INFO - mirror: https://anorien.csc.warwick.ac.uk/mirrors/CTAN/
INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex/contrib/abntex2/tex/abntex2.cls
INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex/contrib/abntexto/abntexto.cls
INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex2e/contrib/abntex2/tex/abntex2.cls
INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex2e/contrib/abntexto/abntexto.cls
INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex/contrib/abntex2/tex/abntex2.cls
INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex/contrib/abntexto/abntexto.cls
INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex2e/contrib/abntex2/tex/abntex2.cls
INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex2e/contrib/abntexto/abntexto.cls
INFO - match count: 8
INFO - directories searched count: 300
INFO - directories ignored count: 20102
INFO - output written to myfile1.txt
INFO - time: 59.2872476309999
```
and the output is written to `myfile1.txt`.

## positional (required) argument
There is one positional (required) option, which is the pattern that you are trying to match. For example
```
ctan-scraper.py ".*?\.cls"
```
will match all files ending with `.cls`. This will take a very long time to run, I recommend referencing
the [ctan root directory](https://anorien.csc.warwick.ac.uk/mirrors/CTAN/) and being more specific 
with the `--path` option, for example
```
ctan-scraper.py --path "macros/latex/contrib/abnt/" ".*?\.cls"
```
## options
* `--logging=<logging mode>`, which has to be one of `['debug','info','warning','error','critical','quiet','verbose']` (default is `INFO`)
* `--mirror=<ctan mirror>`, optionally details the ctan mirror to be used; default is [https://anorien.csc.warwick.ac.uk/mirrors/CTAN/](https://anorien.csc.warwick.ac.uk/mirrors/CTAN/)
* `--output=<output file>`, specifies the file to which the the output will be written (no default)
* `--path=</directory/path >`, for example `--path "macros/latex/contrib/abnt/"` will only search directories matching 
this path, and their subdirectories (no default)

## helpful links
* [ctan root directory](https://anorien.csc.warwick.ac.uk/mirrors/CTAN/)
