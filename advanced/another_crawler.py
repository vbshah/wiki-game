# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 23:05:57 2019

@author: Vaibhav Shah
"""

import requests
from bs4 import BeautifulSoup
from time import sleep, time
from random import randint
import pymongo
import sys

def fetch_connected_urls(url):
    global make_it_stop, target
    url = 'https://en.wikipedia.org' + url
    print('fetching', url)
    while True:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code != 200:
                print('bad request', url)
                return []
            break
        except:
            sleep(randint(10, 100))
            print('trying again')
    soup = BeautifulSoup(r.text, 'html.parser')
    links = []
    for link in soup.findAll('a', href=True):
#        print('link before', link)
        link = link['href']
#        print('link', link)
        if link.lower() == target.lower():
            make_it_stop = True
            break
        if link.startswith('/wiki/'):
            links.append(link)
    return links


def initialize_mongo():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    stratifyd = client['stratifyd']
    priority_queue = stratifyd["priority_queue"]
    graph = stratifyd["graph"]
    
    # fresh start
    priority_queue.delete_many({})
    graph.delete_many({})

    return graph, priority_queue

def set_hashed_index(collection, field):
    collection.create_index([(field, pymongo.HASHED)])

def set_binary_index(collection, field):
    collection.create_index([(field, pymongo.ASCENDING)])

def insert_pq(priority_queue, link, priority=3):
    # adding link of highest priority, first link
    priority_queue.insert_one({'url': link, 'priority': priority})

def clean_queue(priority_queue):
    priority_queue.delete_many({})

def in_graph(graph, url):
    result = list(graph.find({'url': url}).limit(1))
    if len(result) >= 1:
        return True
    else:
        return False

def insert_in_graph(graph, link, connected_links):
    graph.insert_one({'url': link, 'links': connected_links})

def pop_top(priority_queue):
    top_element = priority_queue.find().sort('priotity', -1).limit(1)[0]
    priority_queue.delete_one({'_id': top_element['_id']})
    return top_element

if len(sys.argv) != 3:
    # first, check all arguments are passed
    print('Please pass 2 arguments:')
    print('(1) source page and (2) target page')
    sys.exit()
else:
    source = sys.argv[1]
    target = sys.argv[2]
    
source = '/wiki/' + source.replace(' ', '_')
target = '/wiki/' + target.replace(' ', '_')  # because urls in page have underscore instead of space

make_it_stop = False  # to ensure to stop before extra step
start = time()

# initialize mongodb
graph, priority_queue = initialize_mongo()
set_hashed_index(graph, 'url')
set_binary_index(priority_queue, 'priority')

source_links = fetch_connected_urls(source)
target_links = fetch_connected_urls(target)
source_set = set(source_links)
target_set = set(target_links)


if priority_queue.count_documents({}) == 0:  # starting program from top
    insert_pq(priority_queue, source)

while priority_queue.count_documents({}) > 0:
    top_element = pop_top(priority_queue)
    current_url = top_element['url']
    if in_graph(graph, current_url):
        print('already in graph')
        continue
    else:
        if current_url == target:
            print('found it!')
            break
        else:
            connected_links = fetch_connected_urls(current_url)
            insert_in_graph(graph, current_url, connected_links)
            connected_set = set(connected_links)
            priority = len(source_set & connected_set) + len(target_set & connected_set)
            
            for link in connected_links:
                insert_pq(priority_queue, link, priority)


#lean_queue(priority_queue)

end = time()
print('execution time', end-start)