import caching
import csv
import re
import sys
from bs4 import BeautifulSoup

GET = caching.get_soup
BASE_URL = "http://oireachtasdebates.oireachtas.ie"
TEST_URL = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/dail2013011600001?opendocument"
START_URL = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/datelist?readform&chamber=dail&year=2013"

NUM_QS = {}

def count_questions_asked():
    """ Count number of questions for all TDs. """
    url = START_URL
    soup = GET(url)

    links = soup("a", text = re.compile(r"^\d{2}$"))

    for link in links:
        date_url = BASE_URL + link['href']
        parse_date(date_url)

    return dict_to_array()

def dict_to_array():
    """ Convert dict to array of dicts.  """
    questions_arr = []
    for key in NUM_QS:
        entry = {"name": key.encode("utf-8"),
                "num_questions": NUM_QS[key]}
        questions_arr.append(entry)

    return questions_arr

def get_question_pages(start_soup):
    """ Find start and end pages for priority questions. """
    pqs_p = start_soup.find("p", text = "Priority Questions")
    
    if pqs_p:
        start_link = pqs_p("a")[0]["href"]
        end_p = pqs_p.findNext("p", {"class": "tocitem"})
        end_link = end_p("a")[0]["href"]
        start_page = get_page_num(start_link)
        end_page = get_page_num(end_link)
        return [start_page, end_page]

    return []

def create_url(start_url, page_num):
    """ Create properly formated url given page number. """
    format_page_num = str(page_num).zfill(5)
    url = re.sub(r"\d{5}\?", format_page_num + "?", start_url)
    return url

def get_page_num(url):
    """ Get page number from a URL. """
    page_string = re.findall(r"(\d{5})\?", url)[0]
    page_num = int(page_string)
    return page_num


def parse_date(start_url):
    """ Count questions asked on given day. """
    soup = GET(start_url)
    question_pages = get_question_pages(soup)

    if question_pages:
        #if "Other Questions" not in soup.text:
            #print "__ ", start_url

        start_page, end_page = question_pages
        urls = [create_url(start_url, num) 
                for num in range(start_page, end_page)]

        for url in urls:
            parse_page(url)

        last_page = create_url(start_url, end_page)
        parse_last_page(last_page)

def parse_page(url):
    """ Parse individual debate page, counting questions asked by each TD. """
    soup = GET(url)
    askers = get_askers(soup)
    count_qs(askers)

def parse_last_page(url):
    """ The last page is formatted slightly differently. """
    soup = process_last_page(url)
    askers = get_askers(soup)
    count_qs(askers)

def process_last_page(url):
    """ Process last page before parsing. """
    content = caching.get_content(url)
    soup = BeautifulSoup(content)

    divider = soup.h3
    last_section = content.rsplit(str(divider),1)[0]
    last_soup = BeautifulSoup(last_section)

    return last_soup

def get_askers(soup):
    """ Parses any question askers names from soup. """
    askers = parse_names(soup)
    return askers

def parse_names(soup):
    """ Parses any question askers names from soup. """
    text = soup.text
    names = re.findall(ur"\d+\.\xa0Deputy (.*?)[\xa0]+asked", text, re.U)
    return names

def count_qs(names):
    """ Increment questions asked for each name. """
    for name in names:
        if name in NUM_QS:
            NUM_QS[name] += 1
        else:
            NUM_QS[name] = 1

def dicts_to_csv(dicts, filename):
    """ Outputs a list of dicts to filename. """
    f = open(filename, 'wb')
    keys = dicts[0].keys()
    keys.sort()
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writer.writerow(keys)
    dict_writer.writerows(dicts)

if __name__ == '__main__':
    out_file = sys.argv[1]
    question_data = count_questions_asked()
    dicts_to_csv(question_data, out_file)
