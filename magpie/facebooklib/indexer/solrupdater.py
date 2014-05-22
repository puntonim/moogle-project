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
        tweet = dict()
        tweet['bearertoken_id'] = self.bearertoken_id
        tweet['id'] = redis_entry.id
        tweet['from_id'] = redis_entry.from_id
        tweet['from_name'] = redis_entry.from_name
        tweet['type'] = redis_entry.type
        tweet['created_time'] = facebook_date_to_solr_date(redis_entry.created_time)
        tweet['updated_time'] = facebook_date_to_solr_date(redis_entry.updated_time)
        tweet['message_original'] = redis_entry.message
        tweet['message_clean'] = redis_entry.message_clean

        # Remove entries whose value is None
        tweet = {key: value for (key, value) in tweet.items() if value is not None}

        log.debug('Sending to Solr:\n{}'.format(json.dumps(tweet, indent=4)))

        return tweet