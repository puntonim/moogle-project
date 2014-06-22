import logging
import json

from solrupdater import AbstractSolrUpdater
from models import Provider
from utils.dates import facebook_date_to_solr_date
from utils.solr import CORE_NAMES


log = logging.getLogger('facebook')


class FacebookSolrUpdater(AbstractSolrUpdater):
    """
    Receive a Facebook post, convert it to a document and send it to Solr.

    Parameters:
    bearertoken_id -- a `models.BearerToken.id`.
    """
    CORE_NAME = CORE_NAMES[Provider.NAME_FACEBOOK]

    def _convert_redis_entry_to_solr_doc(self, redis_entry):
        post = dict()
        post['bearertoken_id'] = self.bearertoken_id
        post['id'] = redis_entry.id
        post['from_id'] = redis_entry.from_id
        post['from_name'] = redis_entry.from_name
        post['type'] = redis_entry.type
        post['created_time'] = facebook_date_to_solr_date(redis_entry.created_time)
        post['updated_time'] = facebook_date_to_solr_date(redis_entry.updated_time)
        post['message_original'] = redis_entry.message
        post['message_clean'] = redis_entry.message_clean

        # Remove entries whose value is None
        post = {key: value for (key, value) in post.items() if value is not None}

        log.debug('Sending to Solr:\n{}'.format(json.dumps(post, indent=4)))

        return post