import logging

from ..redislist import RedisTwitterList
from .solrupdater import TwitterSolrUpdater


log = logging.getLogger('twitter')


class TwitterIndexer:
    """
    Indexer to read all tweets stored in Redis for a `bearertoken_id` and send them to Solr.

    Parameters:
    bearertoken_id -- a `models.BearerToken.id`.
    access_token -- a `models.BearerToken.access_token`.
    """

    def __init__(self, bearertoken_id, access_token):
        self.bearertoken_id = bearertoken_id
        self.access_token = access_token

    def run(self):
        redis = RedisTwitterList(self.bearertoken_id)
        solr = TwitterSolrUpdater(self.bearertoken_id)
        for redis_entry in redis.iterate():
            # `redis_entry` is a `RedisTwitterEntry` instance.
            log.debug('Read a tweet from Redis:\n' +
                      'id={}\n'.format(redis_entry.id) +
                      'lang={}\n'.format(redis_entry.lang) +
                      'created_at={}\n'.format(redis_entry.created_at) +
                      'retweeted={}\n'.format(redis_entry.retweeted) +
                      'text={}\n'.format(redis_entry.text) +
                      'text_clean={}\n'.format(redis_entry.text_clean)
            )
            solr.add(redis_entry)
        solr.commit()