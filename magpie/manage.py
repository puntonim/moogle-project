import argparse

from magpie.settings import settings
from models import Provider


def syncdb(args):
    print("Creating the db...")
    from utils.db import setup_db
    setup_db()
    print("Done.")


def loaddata(args):
    print("Loading fixture into the database...")
    from utils.db import loaddata
    import json
    content = json.loads(args.file.read())
    loaddata(content)
    print("Done.")


def shell(args):
    print("Opening a shell and importing all models...")
    from utils.db import Session, get_all_models_classes

    # Import all models
    models_names = []
    for cls in get_all_models_classes():
        model_name = cls.__name__
        models_names.append(model_name)
        globals()[model_name] = getattr(
            __import__('models', fromlist=[model_name]), model_name)

    # Create a new session
    sex = Session()

    # Print some info
    print('')
    print("The following models have been loaded:\n{}".format(models_names))
    print("A session has been open with name `sex`.")
    print("You can run a query like:\n    sex.query({}).all()".format(models_names[0]))
    print('')

    # Start a debug session
    # Try import bpdb (which requires Bpython), if not import plain pdb
    try:
        import bpdb as debug
        # This is a trick to manually import the models because the automatic import of all
        # models works in pdb, but not in bpdb.
        from models import Provider, BearerToken
    except:
        import pdb as debug
    debug.set_trace()
    print("Done.")


def resetindex(args):
    from magpie.settings import settings
    from utils.db import session_autocommit
    from utils.solr import Solr
    from models import BearerToken

    if args.bearertoken_id:
        print("Resetting the Solr index for bearertoken_id: {}".format(args.bearertoken_id))

        with session_autocommit() as sex:
            bearertoken = sex.query(BearerToken).filter_by(id=args.bearertoken_id).one()
            provider_name = bearertoken.provider.name
        query = 'bearertoken_id:{}'.format(args.bearertoken_id)

    if args.provider:
        print("Resetting the Solr index for provider: {}".format(args.provider))
        provider_name = args.provider
        query = '*:*'

    solr = Solr(settings.CORE_NAMES[provider_name])
    solr.delete_by_query(query)
    solr.commit()
    print("Done.")


def flushredis(args):
    print("Flushing Redis keys...")
    from utils.redis import open_redis_connection
    redis = open_redis_connection()
    redis.flushall()
    print('Done.')


def update(args):
    print("Fetching updates for bearertoken_id: {}".format(args.bearertoken_id))
    from updater import UpdateManager

    updater = UpdateManager(args.bearertoken_id, args.reset_cursor)
    updater.run()

    print("Done.")


if __name__ == '__main__':
    provider_names = list(Provider.NAME_CHOICES)
    provider_names.append('all')

    parser = argparse.ArgumentParser(description="Run magpie commands.")
    subparsers = parser.add_subparsers()

    # `syncdb` subcommand.
    subcmd = subparsers.add_parser('syncdb', help='Create the database.')
    subcmd.set_defaults(func=syncdb)

    # `shell` subcommand.
    subcmd = subparsers.add_parser('shell', help='Open a Python shell with all models imported.')
    subcmd.set_defaults(func=shell)

    # `flushredis` subcommand.
    subcmd = subparsers.add_parser('flushredis', help='Deletes all keys in Redis.')
    subcmd.set_defaults(func=flushredis)

    # `loaddata` subcommand.
    subcmd = subparsers.add_parser('loaddata', help='Load a json fixture.')
    subcmd.add_argument('file', type=argparse.FileType('r'),
                        help='Path to the json fixture file.')
    subcmd.set_defaults(func=loaddata)

    # `update` subcommand.
    subcmd = subparsers.add_parser('update', help='Fetch updates for a bearertoken_id.')
    subcmd.add_argument('bearertoken_id', type=int,
                        help='The bearertoken_id to fetch updates for.')
    subcmd.add_argument('--reset-cursor', action='store_true',
                        help='Reset the cursor before updating.')
    subcmd.set_defaults(func=update)

    # `resetindex` subcommand.
    subcmd = subparsers.add_parser('resetindex', help='Reset Solr index for a bearertoken_id.')
    #subcmd.add_argument('bearertoken_id', type=int,
    #                    help='The bearertoken_id to reset the Solr index.')
    group = subcmd.add_mutually_exclusive_group(required=True)
    group.add_argument('--bearertoken_id', type=int,
                        help='The bearertoken_id to reset the Solr index for.')
    group.add_argument('--provider', choices=settings.CORE_NAMES.values(),
                       help='The provider to reset the Solr index for.')
    subcmd.set_defaults(func=resetindex)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()