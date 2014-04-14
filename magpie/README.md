MAGPIE
======

Magpie is the backend core engine which powers the Moogle Project.
It crawls and index private data from service providers.
It is powered by Python.

Follow the steps in order to create a *local development* copy.

**NOTE** The project is still in its early stages.


1. Create a project folder in your workspace
--------------------------------------------
    $ mkdir moogle-project
    $ cd moogle-project
We will refer to this folder as *repository root*.


2. Clone the reposiotry
-----------------------
    $ git clone https://github.com/nimiq/moogle-project.git .


3. Create a virtual environment
-------------------------------
### 3.1. Using Virtualenvwrapper
    $ mkvirtualenv magpie

Next set the right settings file and passwords as environment variables.
The passwords are the API client ids and secrets you got while registering your app at the providers website  (see README.md in the main folder).
Virtualenvwrapper hook on activation:

    $ nano ~/.virtualenvs/magpie/bin/postactivate
    # Settings
    export MAGPIE_SETTINGS_MODULE=magpie.settings.local

    # Passwords
    export DRIVE_CLIENT_ID=...
    export DRIVE_CLIENT_SECRET=...
    export GMAIL_CLIENT_ID=...
    export GMAIL_CLIENT_SECRET=...
    export FACEBOOK_CLIENT_ID=...
    export FACEBOOK_CLIENT_SECRET=...
    export TWITTER_CLIENT_ID=...
    export TWITTER_CLIENT_SECRET=...
    export DROPBOX_CLIENT_ID=...
    export DROPBOX_CLIENT_SECRET=...

Virtualenvwrapper hook on deactivation:

    $ nano ~/.virtualenvs/magpie/bin/predeactivate
    # Settings
    unset MAGPIE_SETTINGS_MODULE

    # Passwords
    unset DRIVE_CLIENT_ID
    unset DRIVE_CLIENT_SECRET
    unset GMAIL_CLIENT_ID
    unset GMAIL_CLIENT_SECRET
    unset FACEBOOK_CLIENT_ID
    unset FACEBOOK_CLIENT_SECRET
    unset TWITTER_CLIENT_ID
    unset TWITTER_CLIENT_SECRET
    unset DROPBOX_CLIENT_ID
    unset DROPBOX_CLIENT_SECRET

Now set the right `PYTHONPATH` (user your own *path*):

    add2virtualenv "/Users/my_user/workspace/moogle-project/magpie"

Reactivate the virtual environment:

    $ deactivate
    $ workon magpie

### 3.2. Using plain Virtualenv
    $ virtualenv ve

Next set the right settings file and passwords as environment variables.
The passwords are the API client ids and secrets you got while registering your app at the providers website.
Virtualenv hook on activation (user your own *path* for `PYTHONPATH`):

    $ nano ve/bin/activate
    # PYTHONPATH
    export PYTHONPATH="/Users/my_user/workspace/moogle-project/magpie"

    # Settings
    export MAGPIE_SETTINGS_MODULE=magpie.settings.local

    # Passwords
    export DRIVE_CLIENT_ID=...
    export DRIVE_CLIENT_SECRET=...
    export GMAIL_CLIENT_ID=...
    export GMAIL_CLIENT_SECRET=...
    export FACEBOOK_CLIENT_ID=...
    export FACEBOOK_CLIENT_SECRET=...
    export TWITTER_CLIENT_ID=...
    export TWITTER_CLIENT_SECRET=...
    export DROPBOX_CLIENT_ID=...
    export DROPBOX_CLIENT_SECRET=...

There is no hook on deactivation (not a big issue).

Activate the virtual environment:

    $ source ve/bin/activate


4. Optional: local copy of environment variables (passwords)
------------------------------------------------------------
Optionally make a copy of the environment variables (the passwords) in the file:

    icecreamshop/icecreamshop/settings/vars.environment

This file will be IGNORED by Git, so it will be stored only in your local machine.
You might need it in case you accidentally remove your virtual environment and lose your passwords.


5. Install the requirements
---------------------------
    $ cd magpie
    $ pip install -r magpie/requirements/local.txt


6. Check the settings
---------------------
Check the settings file: `magpie/settings/local.py`


7. Create the db
----------------
    $ python manage.py syncdb


8. Import the fixtures
----------------------
    $ python manage.py loaddata crawlers/fixtures/providers.json

Copy `crawlers/fixtures/sample_bearertoken.json.template` to `crawlers/fixtures/sample_bearertoken.json`.
Add some user's bearer tokens, then import the fixture:

    $ python manage.py loaddata crawlers/fixtures/sample_bearertoken.json
