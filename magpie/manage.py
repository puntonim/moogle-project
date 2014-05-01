#!/usr/bin/env python

import sys
from os import environ
from os.path import join, normpath


if __name__ == '__main__':
    # TODO use argparse
    # See https://github.com/united-academics/uarepocamp/blob/master/campaign/scripts/send_bulk_email2.py

    # TODO delete me
    def _reset_cursor(bearertoken):
        bearertoken.updates_cursor = None

    if sys.argv[1] == 'syncdb':
        """
        Setup the SQLAlchemy db as configured in the settings.
        """
        from utils.db import setup_db
        setup_db()

    elif sys.argv[1] == 'loaddata':
        """
        Load a fixture into the database.
        """
        from utils.db import loaddata
        path = normpath(join(environ['PWD'], sys.argv[2]))
        loaddata(path)

    elif sys.argv[1] == 'shell':
        """
        Start a debug shell and automatically imports the models.
        """
        # TODO it should import from all models.py in all packages

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
        except:
            import pdb
        debug.set_trace()

    elif sys.argv[1] == 'dropbox':
        from dropboxlib.synchronizer import DropboxSynchronizer
        from utils.db import session_autocommit
        from models import Provider

        print("START DROPBOX")

        with session_autocommit() as sex:
            provider = sex.query(Provider).filter_by(name=Provider.NAME_DROPBOX).one()
            bearertoken = provider.bearertokens[0]
            try:
                if sys.argv[2] == 'resetcursor':
                    _reset_cursor(bearertoken)
            except IndexError:
                pass

        DropboxSynchronizer(bearertoken=bearertoken).run()

    elif sys.argv[1] == 'twitter':
        from twitterlib.synchronizer import TwitterSynchronizer
        from utils.db import session_autocommit
        from models import Provider

        print("START TWITTER")

        with session_autocommit() as sex:
            provider = sex.query(Provider).filter_by(name=Provider.NAME_TWITTER).one()
            bearertoken = provider.bearertokens[0]
            try:
                if sys.argv[2] == 'resetcursor':
                    _reset_cursor(bearertoken)
            except IndexError:
                pass

        TwitterSynchronizer(bearertoken=bearertoken).run()

    elif sys.argv[1] == 'facebook':
        from facebooklib.synchronizer import FacebookSynchronizer
        from utils.db import session_autocommit
        from models import Provider

        print("START FACEBOOK")

        with session_autocommit() as sex:
            provider = sex.query(Provider).filter_by(name=Provider.NAME_FACEBOOK).one()
            bearertoken = provider.bearertokens[0]
            try:
                if sys.argv[2] == 'resetcursor':
                    _reset_cursor(bearertoken)
            except IndexError:
                pass

        FacebookSynchronizer(bearertoken=bearertoken).run()


