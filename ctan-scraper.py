#
# reference: 
#   https://anorien.csc.warwick.ac.uk/mirrors/CTAN/
#   https://www.geeksforgeeks.org/beautifulsoup-error-handling/
# 
# test cases
#   python3 ctan-new.py --path "macros/latex/contrib/abnt/"  ".*?\.cls"
#   python3 ctan-new.py --path "macros/latex/contrib/siunitx" --verbose ".*?\.cls"
#   python3 ctan-new.py --path "macros/latex/contrib/siunitx"  ".*?\..*?"
#   python3 ctan-new.py --path "macros/latex/contrib/aeb"  ".*?\.(pdf|tex)"
#   python3 ctan-new.py --path "macros/latex/contrib/enumitem"  "enumitem.sty"
#   python3 ctan-new.py --path "macros/latex/contrib/ab"  ".*\.sty"

from urllib.request import Request, urlopen, urlretrieve
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import argparse, re, logging, timeit

# 
# argument parsing
#
parser = argparse.ArgumentParser(description='ctan web scraper')

# choices=['biblio','digests','dviware','fonts','graphics','help','indexing','info','install','macros','obsolete','support','systems','tds','usergrps','web'],
parser.add_argument('--path', 
                    type=str, 
                    help='path pattern, can be regex')

parser.add_argument('--verbose', action='store_true',
                    help='verbose mode')

parser.add_argument('pattern', 
                    type=str, 
                    help='pattern to match, can be regex')

args = parser.parse_args()

# 
# remove trailing '/'
#
def remove_trailing_slash(url):
   if url[-1] == '/':
       url = url[:-1]
   return url

#
# logger
#   references:
#       https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
#       https://gist.github.com/davidohana/32252f6235a2837a9f43e173784e66c9
#
class CustomFormatter(logging.Formatter):

    green = "\x1b[1;32m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(levelname)s - "+reset+"%(message)s"

    FORMATS = {
        logging.DEBUG: yellow + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

log = logging.getLogger('logger')
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
if args.verbose: 
   ch.setLevel(logging.DEBUG)
else:
   ch.setLevel(logging.INFO)

ch.setFormatter(CustomFormatter())
log.addHandler(ch)

#
# argument work
#
path_patterns = []

if args.path:
   # remove any trailing '/'
   args.path = remove_trailing_slash(args.path)

   path_patterns = args.path.split("/")
   path_patterns[:] = [re.compile(rf"{x}") for x in path_patterns]
   log.info(path_patterns)

prog = re.compile(rf"^{args.pattern}$")

ignore_count = 0
accept_count = 0
match_count = 0

# read url routine
#   reference: https://stackoverflow.com/a/40661485
#
def read_url(url,pattern,level):
    global ignore_count
    global accept_count
    global match_count 

    url = url.replace(" ","%20")
    req = Request(url)

    # try and read the URL, otherwise exit
    try:
       a = urlopen(req).read()
    except HTTPError:
       return

    # parse the page
    soup = BeautifulSoup(a, 'html.parser')

    # loop through the links <a>
    all_links_list = (soup.find_all('a'))
    for indv_link in all_links_list[:]:
        file_name = indv_link.extract().get_text()
        if re.match(r'^[a-zA-Z]+$',file_name):
           file_name += '/'
        url_new = url + file_name

        # ignore URLs that have spaces
        if ( (" " in url_new) or (":" in file_name)):
           continue

        if (level < len(path_patterns)) and not path_patterns[level].match(file_name):
           file_name = remove_trailing_slash(file_name)

           #   https://stackoverflow.com/questions/1207406/how-to-remove-items-from-a-list-while-iterating
           all_links_list[:] = [x for x in all_links_list if not x==indv_link]

           log.debug('IGNORE: '+url_new)
           ignore_count += 1
           continue

        # otherwise proceed
        log.debug('*ACCEPT: '+url_new)
        accept_count += 1

        try:
           if( file_name[-1] == '/' and file_name[0] != '.' ):
               next_level = level+1
               read_url(url_new,pattern,next_level)
        except IndexError:
           continue

        if prog.match(file_name):
           log.info(url_new)
           match_count += 1

ctan_mirror = "https://anorien.csc.warwick.ac.uk/mirrors/CTAN/"
log.info('mirror: '+ctan_mirror)
t0 = timeit.default_timer()
read_url(ctan_mirror,args.pattern,0)
t1 = timeit.default_timer()
log.info(f'match count: {match_count}')
log.info(f'directories searched count: {accept_count}')
log.info(f'directories ignored count: {ignore_count}')
log.info(f'time: {t1-t0}')
