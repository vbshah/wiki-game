I have created this program "another_crawler.py" as an advnaced implementation. I have not completely verified 
this code but main logic of finding target is same as "wikipedia_game.py". 

This program is created as an example of "production-ready" code. I have used mongoDB as a graph and priority queue.

I have divided most of the functionality as a method so it can also be replaced by data structures of Python.

Here's my presentation of database:

collection: graph: {url: Listof[urls]}. Here, url is hashed key so it can be easily be searched, just like 
graph data structure.

collection: priority_queue: {url:priority}. Here, I have set priority as binary index so it can be easily 
be found. Insertion time and search time will be log(n).

Note: this code is currently slower than "wikipedia_game.py". The reason is that it requires lots of IO operations.
But, if we can make if hybrid, by keeping data both in database and in-memory, it will be faster.
We can do read operation from memeory and perform all write operation in database. The reason to keep database is,
when program crashes all of a sudden, it doesnot have to go back and start again. It can pop top priority page and
start working again.
