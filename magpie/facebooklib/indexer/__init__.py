import logging

from ..redislist import RedisFacebookList
from .solrupdater import FacebookSolrUpdater


log = logging.getLogger('facebook')


class FacebookIndexer:
    """
    Read all Facebook posts stored in Redis for a `bearertoken_id` and send them to Solr.

    Parameters:
    bearertoken_id -- a `models.BearerToken.id`.
    access_token -- a `models.BearerToken.access_token`.
    """
    def __init__(self, bearertoken_id, access_token):
        self.bearertoken_id = bearertoken_id
        self.access_token = access_token

    def run(self):
        redis = RedisFacebookList(self.bearertoken_id)
        solr_updater = FacebookSolrUpdater(self.bearertoken_id)
        for redis_entry in redis.iterate():
            # `redis_entry` is a `RedisFacebookEntry` instance.
            log.debug('id={}\n'.format(redis_entry.id) +
                      'from_name={}\n'.format(redis_entry.from_name) +
                      'from_id={}\n'.format(redis_entry.from_id) +
                      'type={}\n'.format(redis_entry.type) +
                      'created_time={}\n'.format(redis_entry.created_time) +
                      'updated_time={}\n'.format(redis_entry.updated_time) +
                      'message={}\n'.format(redis_entry.message) +
                      'message_clean={}\n'.format(redis_entry.message_clean)
            )
            solr_updater.add(redis_entry)
        solr_updater.commit()