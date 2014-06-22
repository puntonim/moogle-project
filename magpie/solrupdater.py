from abc import ABCMeta, abstractmethod

from utils.solr import Solr


class AbstractSolrUpdater(metaclass=ABCMeta):
    """
    Receive an item like a Twitter tweet, a Facebook post, a Dropbox file, etc., convert it to
    a document and send it to Solr.

    Parameters:
    bearertoken_id -- a `models.BearerToken.id`.
    """
    def __init__(self, bearertoken_id):
        self.bearertoken_id = bearertoken_id
        self.solr = Solr(self.CORE_NAME)

    def add(self, redis_entry, commit=False):
        doc = self._convert_redis_entry_to_solr_doc(redis_entry)

        self.solr.update([doc], 'json', commit)

    def commit(self):
        self.solr.commit()

    @abstractmethod
    def _convert_redis_entry_to_solr_doc(self, redis_entry):
        pass