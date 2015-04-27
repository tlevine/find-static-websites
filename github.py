#!/usr/bin/env python3
import requests
from lxml.html import fromstring
from vlermv import cache

HEADERS = {
    'user-agent': 'http://dada.pink/find-static-websites/'
}

def main():
    import csv, sys
    w = csv.writer(sys.stdout)
    w.writerow(('domain', 'source_code'))
    for line in sys.stdin:
        domain = line.strip()
        if is_gh_pages(domain):
            w.writerow((domain, gh_url(domain)))

def is_gh_pages(x):
    try:
        r = download_domain(x)
    except requests.exceptions.ConnectionError:
        return False
    else:
        return parse_domain(r)

def gh_url(x):
    return parse_github_search(download_github_search(x))

@cache('~/.find-static-websites/domain')
def download_domain(domain):
    return requests.head('http://%s/' % domain, headers = HEADERS)

def parse_domain(response):
    return response.headers['server'] == 'GitHub.com'

@cache('~/.find-static-websites/github_search')
def download_github_search(domain):
    url = 'https://github.com/search'
    params = {
        'utf8': '✓',
        'q': 'in:/ %s filename:CNAME&type=Code' % domain,
    }
    return requests.get(url, params = params, headers = HEADERS)

def parse_github_search(response):
    html = fromstring(response.text)
    html.make_links_absolute(response.url)
    hrefs = html.xpath('id("code_search_results")/descendant::p[@class="title"]/a[position()=1]/@href')
    if len(hrefs) > 0:
        return str(hrefs[0])

if __name__ == '__main__':
    main()
