#!/bin/bash

# ctan-scraper.py test-cases script to ensure that, as much as possible, 
# the script behaves as intended.
#

set -x
ctan-scraper.py --path "macros/latex/contrib/abnt/" --output myfile1.txt ".*?\.cls"
ctan-scraper.py --path "macros/latex/contrib/siunitx" --output myfile2.txt ".*?\.cls"
ctan-scraper.py --path "macros/latex/contrib/siunitx" --output myfile3.txt ".*?\..*?"
ctan-scraper.py --path "macros/latex/contrib/aeb" --output myfile4.txt ".*?\.(pdf|tex)"
ctan-scraper.py --path "macros/latex/contrib/enumitem" --output myfile5.txt "enumitem.sty"
ctan-scraper.py --path "macros/latex/contrib/ab" --output myfile6.txt ".*\.sty"
set +x

exit 0
