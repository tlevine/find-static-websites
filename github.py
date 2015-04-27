#!/usr/bin/env python3
import re

import requests
from lxml.html import fromstring
from vlermv import cache

HEADERS = {
    'user-agent': 'http://dada.pink/find-static-websites/'
}

def main():
    import csv, sys
    if len(sys.argv) == 1:
        w = csv.writer(sys.stdout)
        w.writerow(('domain', 'source_code'))
        for line in sys.stdin:
            domain = _extract_domain(line.strip())
            sys.stderr.write('Checking %s\n' % domain)
            if is_gh_pages(domain):
                sys.stderr.write('%s is on GitHub pages, looking for source code\n' % domain)
                w.writerow((domain, gh_url(domain)))
    else:
        at_least_one = False
        for url in sys.argv[1:]:
            domain = _extract_domain(url)
            if is_gh_pages(domain):
                sys.stdout.write(gh_url(domain) + '\n')
                at_least_one = True
        if not at_least_one:
            sys.stderr.write('No matches\n')
            sys.exit(1)

def _extract_domain(url):
    '''
    >>> _extract_domain('https://thomaslevine.com')
    thomaslevine.com
    '''
    return re.sub(r'https?://([^/]+).*', r'\1', url)

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
    return requests.head('http://%s/' % domain, headers = HEADERS, allow_redirects = True)

def parse_domain(response):
    return response.headers.get('server') == 'GitHub.com'

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
