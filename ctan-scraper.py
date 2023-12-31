#!/usr/bin/python3
#
# ctan-scraper.py
#
#   a script to web scrape ctan for a user specified pattern
# 
# example
# 
#       ctan-scraper.py --path "macros/latex/contrib/abnt/" --output myfile1.txt ".*?\.cls"
# 
# gives all of the `.cls` files in the directory `<mirror>/macros/latex/contrib/abnt/`, and
# you receive
# 
#       INFO - [re.compile('macros'), re.compile('latex'), re.compile('contrib'), re.compile('abnt')]
#       INFO - mirror: https://anorien.csc.warwick.ac.uk/mirrors/CTAN/
#       INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex/contrib/abntex2/tex/abntex2.cls
#       INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex/contrib/abntexto/abntexto.cls
#       INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex2e/contrib/abntex2/tex/abntex2.cls
#       INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex2e/contrib/abntexto/abntexto.cls
#       INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex/contrib/abntex2/tex/abntex2.cls
#       INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex/contrib/abntexto/abntexto.cls
#       INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex2e/contrib/abntex2/tex/abntex2.cls
#       INFO - https://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex2e/contrib/abntexto/abntexto.cls
#       INFO - match count: 8
#       INFO - directories searched count: 300
#       INFO - directories ignored count: 20102
#       INFO - output written to myfile1.txt
#       INFO - time: 59.2872476309999
# 
# and the output is written to `myfile1.txt`.
#
from urllib.request import Request, urlopen, urlretrieve
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import argparse, re, logging, timeit

# 
# argument parsing
#
parser = argparse.ArgumentParser(description='ctan web scraper')

# choices=['biblio','digests','dviware','fonts','graphics','help','indexing','info','install','macros','obsolete','support','systems','tds','usergrps','web'],

parser.add_argument('--logging', 
                    type=str.lower, 
                    choices=['debug','info','warning','error','critical','quiet','verbose'],
                    help='logging choice')

parser.add_argument('--mirror', 
                    type=str, 
                    help='ctan mirror')

parser.add_argument('--output', 
                    type=str, 
                    help='output file')

parser.add_argument('--path', 
                    type=str, 
                    help='path pattern, can be regex')

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
if args.logging: 
   if args.logging == 'info':
      ch.setLevel(logging.INFO)
   elif (args.logging == 'debug' or args.logging == 'verbose'):
      ch.setLevel(logging.DEBUG)
   elif args.logging == 'warning':
      ch.setLevel(logging.WARNING)
   elif args.logging == 'error':
      ch.setLevel(logging.ERROR)
   elif (args.logging == 'critical' or args.logging == 'quiet'):
      ch.setLevel(logging.CRITICAL)
   else:
      ch.setLevel(logging.INFO)
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

ctan_pattern = re.compile(rf"^{args.pattern}$")

ignore_count = 0
accept_count = 0

match_storage = []

# read url routine
#   reference: https://stackoverflow.com/a/40661485
#
def read_url(url,pattern,level):
    global ignore_count
    global accept_count

    # https://www.geeksforgeeks.org/beautifulsoup-error-handling/
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

        if ctan_pattern.match(file_name):
           log.info(url_new)
           match_storage.append(url_new)

#
# possibly read in user-specified mirror
#
if args.mirror: 
   ctan_mirror = args.mirror
else:
   ctan_mirror = "https://anorien.csc.warwick.ac.uk/mirrors/CTAN/"
log.info('mirror: '+ctan_mirror)

#
# the main routine
#
t0 = timeit.default_timer()
read_url(ctan_mirror,args.pattern,0)
t1 = timeit.default_timer()
log.info(f'match count: {len(match_storage)}')
log.info(f'directories searched count: {accept_count}')
log.info(f'directories ignored count: {ignore_count}')

# 
# output to file
#
if args.output: 
  ctan_scrape_file = open(args.output, "w")
  for indv_match in match_storage:
      ctan_scrape_file.write(indv_match+"\n")
  ctan_scrape_file.close()
  log.info(f'output written to {args.output}')

log.info(f'time: {t1-t0}')
