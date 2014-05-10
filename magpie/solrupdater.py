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
        doc = self._convert_redis_entry_to_solr_doc(redis_entry)

        r = self.solr.update([doc], 'json', commit)
        self._sanity_check(r, True)

        if commit:
            self.commit()

    @abstractmethod
    def _convert_redis_entry_to_solr_doc(self, redis_entry):
        pass

    @staticmethod
    def _sanity_check(r, is_check_solr_response=False):
        if r.status != 200:
            raise SolrResponseError('HTTP Status: {}\n{}'.format(
                r.status, r.raw_content)
            )

        if is_check_solr_response:
            if r.solr_status != 0:
                raise SolrResponseError('Solr Status: {}\n{}'.format(
                    r.solr_status, r.raw_content)
                )

    def commit(self):
        r = self.solr.commit()
        self._sanity_check(r)