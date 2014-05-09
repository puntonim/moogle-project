from abc import ABCMeta, abstractmethod

from utils.solr import open_solr_connection
from utils.exceptions import SolrResponseError


class AbstractSolrUpdater(metaclass=ABCMeta):
    """
    Receive an item like a Twitter tweet, a Facebook post, a Dropbox file, etc., convert it to
    a document and send it to Solr.

    Parameters:
    bearertoken_id -- a `models.BearerToken.id`.
    """
    def __init__(self, bearertoken_id):
        self.bearertoken_id = bearertoken_id
        self.solr = open_solr_connection(self.CORE_NAME)

    def add(self, redis_entry, commit=False):
        doc = self._convert_redis_entry_to_solr_entry(redis_entry)

        r = self.solr.update([doc], 'json', commit)
        self._sanity_check(r)
        if r.status != 200 or r.solr_status != 0:
            raise Exception

        if commit:
            self.solr.commit()

    @abstractmethod
    def _convert_redis_entry_to_solr_entry(self, redis_entry):
        pass

    @staticmethod
    def _sanity_check(r):
        if r.status != 200 or r.solr_status != 0:
            raise SolrResponseError('HTTP Status: {}\nSolr Status: {}'.format(r.status,
                                                                              r.solr_status))

    def commit(self):
        self.solr.commit()