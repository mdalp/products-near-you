1. How would your design change if the data was not static (i.e updated frequently
during the day)?

I would definitely use a database that handles GEO data, e.g. PostgreSQL, or
a tool optimised for GEO indexes.
If, for some reason, I can't rely on those, I'd use a R-Tree to index the data
myself https://en.wikipedia.org/wiki/R-tree.

2. Do you think your design can handle 1000 concurrent requests per second? If not, what
would you change?
I doubt my design can handle 1000 requests per second. My solution is made to
keep everything separate and to keep indexes between "tables" but it's not
fully optimised for speed.
What I'd do is to:
 - use the right tool to store the data (e.g.: PostgreSQL)
 - try to run my code on PyPy
 - cache more aggressively (especially TODO in `IndexedAggregator.__getitem__`)
 - I'd replicate data in `IndexedAggregator` instead of referencing everything via `id`
