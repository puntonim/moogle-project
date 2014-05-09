import logging
import json
from time import strptime, mktime
from datetime import datetime

from solrupdater import AbstractSolrUpdater
from models import Provider
from magpie.settings import settings


log = logging.getLogger('twitter')


class TwitterSolrUpdater(AbstractSolrUpdater):
    """
    Receive a tweet, convert it to a document and send it to Solr.

    Parameters:
    bearertoken_id -- a `models.BearerToken.id`.
    """
    CORE_NAME = settings.CORE_NAMES[Provider.NAME_TWITTER]

    def _convert_redis_entry_to_solr_entry(self, redis_entry):
        tweet = dict()
        tweet['bearertoken_id'] = self.bearertoken_id
        tweet['id'] = redis_entry.id
        tweet['lang'] = redis_entry.lang
        tweet['retweeted'] = redis_entry.retweeted
        tweet['text_original'] = redis_entry.text
        tweet['text_clean'] = redis_entry.text_clean

        # Convert created_at (Twitter format: Sun Feb 23 10:49:52 +0000 2014) to a datetime
        dt = redis_entry.created_at
        dt = strptime(dt, '%a %b %d %H:%M:%S +0000 %Y')
        dt = datetime.fromtimestamp(mktime(dt))
        # Convert datetime to Solr format: 2014-02-23T10:49:52Z
        tweet['created_at'] = '{}Z'.format(dt.isoformat())

        # Remove entries whose value is None
        tweet = {key: value for (key, value) in tweet.items() if value is not None}

        log.debug('Sending to Solr:\n{}'.format(json.dumps(tweet, indent=4)))

        return tweet