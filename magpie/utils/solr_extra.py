"""
Extraordinary operations on Solr.
In order to use it, write temporary client code in `manage.py`, f.i. you can temporary rewrite
the mock `ping` command.
"""
from .solr import Solr


def change_bearertoken_by_query(core, query, new_bearertoken):
    solr = Solr(core)

    cursor = solr.search_cursor(q=query)
    new_docs = list()

    for r in cursor.fetch(100):
        for doc in r.documents:
            new_docs.append({'id': doc['id'], 'bearertoken_id': new_bearertoken})

    solr.update(new_docs, 'json')
    solr.commit()
