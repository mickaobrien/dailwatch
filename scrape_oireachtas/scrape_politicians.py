import caching
import csv
import sys

GET = caching.get_soup
BASE_URL = 'http://www.oireachtas.ie/members-hist/'
LIST_URL = BASE_URL + 'default.asp?housetype=0&HouseNum=31&disp=mem'
TEST_URL = 'http://www.oireachtas.ie/members-hist/default.asp?housetype=0&HouseNum=30&MemberID=535&ConstID=181'

def scrape_data():
    """ Scrape all politician data. """
    politicians = []

    links = get_links(LIST_URL)
    for link in links:
        politicians.append(get_history(link))

    return politicians
    
def get_links(url):
    """ Get list of all links to politician pages. """
    soup = GET(url)
    politicians = soup.find('ul', {'id': 'memberslist'}).findAll('li')
    links = []

    for politician in politicians:
        link = BASE_URL + politician.find('a')['href']
        links.append(link)

    return links

def get_history(url):
    """ Get history from individual politician page. """
    soup = GET(url)

    name = soup.find('h3').text.split(' ', 1)[1].encode('utf-8')

    terms = soup.findAll('ul', {'style': 'list-style-type:none;'})
    num_terms = len(terms)

    # the layout is different for first time TDs vs those with multiple terms
    # so if num_terms==0, that means it's a first time TD
    if num_terms == 0:
        
        num_terms = 1
        years_served = 5

    else:
        years_served = 0

        for term in terms:
            span = term.findAll('li')[2].text.strip().split()[1]
            num_years = length_of_span(span)
            years_served += num_years

    politician = {'name': name, 
                  'number_terms': num_terms, 
                  'years_served': years_served}

    return politician
    

def length_of_span(span):
    """ Converts e.g. '2011-2016' to 5. """
    start, end = map(int, span.split('-'))
    length = end - start
    return length


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
    politicians = scrape_data()
    dicts_to_csv(politicians, out_file)
