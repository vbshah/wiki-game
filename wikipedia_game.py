# -*- coding: utf-8 -*-
"""
Created on Mon Oct 7 23:05:57 2019

@author: Vaibhav Shah
"""

import requests
from bs4 import BeautifulSoup
from time import sleep, time
from random import randint
from queue import PriorityQueue
import sys

def fetch_connected_urls(url):
    """
        descrption: this method returns all the wikipedia urls on a given page
        Note: the URL has to be in format of '/wiki/page_title'
        
        parameters:
            url: URL to fetch
        returns:
            list of URLs
    """
    url = 'https://en.wikipedia.org' + url.replace(' ', '_')
    print('fetching', url)
    r = None
    for i in range(10):
        try:
            r = requests.get(url)
            if r.status_code != 200:
                print('bad request', url)
                return
            break
        except:
            print('trying again')
            sleep(randint(1, 10)/10)
            
    if r is None:
        return []
    soup = BeautifulSoup(r.text, 'html.parser')
    links = []
    for link in soup.findAll('a', href=True):
#        print('link before', link)
        link = link['href']
#        print('link', link)
        if link.startswith('/wiki/'):
            links.append(link)
    return links


if len(sys.argv) != 3:
    # first, check all arguments are passed
    print('Please pass 2 arguments:')
    print('(1) source page and (2) target page')
    source = "Web Bot"
    target = "Tax Holiday"
#    sys.exit()
else:
    source = sys.argv[1]
    target = sys.argv[2]
    
start_time = time()  # when program starts
source = source.capitalize()
target = target.capitalize()
base_url = '/wiki/'  # given url won't have /wiki argument
source_link = base_url + source
target_link = base_url + target
source_link = source_link.replace(' ', '_')
target_link = target_link.replace(' ', '_')
source_links = fetch_connected_urls(source_link)
target_links = fetch_connected_urls(target_link)
source_set = set(source_links)
target_set = set(target_links)

# todo: add target condition

graph = dict()
queue = PriorityQueue()
queue.put((1, source_link))

# to find path
prev = dict()   # key: current, val: prev. 1-1 value
min_distance = dict()   # minimum distance to the node from source
min_distance[source_link] = 0

while queue.qsize() > 0:
    _, current_link = queue.get()  # get top priority next node from priority queue
    if current_link in graph:
        continue
    if current_link.lower() == target_link.lower().replace(' ', '_'):
        print('found it!')
        break
    connected_links = fetch_connected_urls(current_link)
    graph[current_link] = connected_links

    connected_set = set(connected_links)
#    priority = len(web_bot_set & connected_set) + 2*len(tax_holiday_set & connected_set)
    """
        # this is my main logic to go closer to target page.
        # Even if I travel directly, just for the path of 4 pages. In BFS,
        # I have to travel 100 million pages (10**8) as average page on wikipedia
        # has 100 pages. So, I am giving higher priority to the page which is more 
        # closer to target page. So, it has to travel less pages.
        # For the given example, this program had to travel 1116 pages which is fine.
    """
    priority = len(target_set & connected_set) ** 2

    for link in connected_links:
        """
            # Priority queue in Python gets value in reverse. 
            # So, adding values with negative will give actual top value
        """
        if link != current_link:
            queue.put((-priority, link))
        else:
            continue
        if link not in prev:    # if we have calculated distance for the link page, compare again            
            prev[link] = current_link
            min_distance[link] = min_distance[current_link] + 1
        else:   # Just add the distance = previous node's distance + 1
            current_min_dist = min_distance[link]
            if min_distance[current_link] + 1 < current_min_dist:
                min_distance[link] = min_distance[current_link] + 1
                prev[link] = current_link

end_time = time()    # crawling is over

graph[target_link] = fetch_connected_urls(target_link)
print('total time in minutes', (end_time-start_time)/60)

"""
    # Till now, I have calculated best previous page for each page.
    # So, we can travel in reverse and reach to our source page. 
    # This will be the best path.
"""
current = target_link.replace(' ', '_')
path = []
while current != source_link:
    print('current', current)
    path.append(current.replace('/wiki/', ''))  # removing /wiki/ from link
    current = prev[current]
#    if len(path) > 10:
#        break

path.append(source_link.replace('/wiki/', ''))
path = [page.capitalize().replace('_', ' ') for page in path][::-1]   # reversing
print(' -> '.join(path))
