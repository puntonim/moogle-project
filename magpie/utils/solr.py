from mysolr import Solr

from magpie.settings import settings


solr = Solr(settings.SOLR_URL)


def open_solr_connection():
    return solr