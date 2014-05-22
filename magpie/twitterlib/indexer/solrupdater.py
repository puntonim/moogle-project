import logging
import json

from solrupdater import AbstractSolrUpdater
from models import Provider
from utils.dates import twitter_date_to_solr_date
from utils.solr import CORE_NAMES


log = logging.getLogger('twitter')


class TwitterSolrUpdater(AbstractSolrUpdater):
    """
    Receive a tweet, convert it to a document and send it to Solr.

    Parameters:
    bearertoken_id -- a `models.BearerToken.id`.
    """
    CORE_NAME = CORE_NAMES[Provider.NAME_TWITTER]

    def _convert_redis_entry_to_solr_doc(self, redis_entry):
        tweet = dict()
        tweet['bearertoken_id'] = self.bearertoken_id
        tweet['id'] = redis_entry.id
        tweet['lang'] = redis_entry.lang
        tweet['retweeted'] = redis_entry.retweeted
        tweet['text_original'] = redis_entry.text
        tweet['text_clean'] = redis_entry.text_clean
        tweet['created_at'] = twitter_date_to_solr_date(redis_entry.created_at)

        # Remove entries whose value is None
        tweet = {key: value for (key, value) in tweet.items() if value is not None}

        log.debug('Sending to Solr:\n{}'.format(json.dumps(tweet, indent=4)))

        return tweet