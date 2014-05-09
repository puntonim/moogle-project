from mysolr import Solr

from magpie.settings import settings


_solr = None


def open_solr_connection(core_name):
    global _solr
    if not _solr:
        url = '{}/{}'.format(settings.SOLR_URL, core_name)
        _solr = Solr(url)
    return _solr