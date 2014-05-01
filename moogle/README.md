MOOGLE
======

Moogle is the website which provides the main user interface to the Moogle Project.
It is powered by Django, a Python web framework.

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
You can create virtual environments using Virtualenvwrapper or Virtualenv.
I usually use Virtualenvwrapper in development and Virtualenv in production.

### 3.1. Using Virtualenvwrapper
    $ mkvirtualenv moogle

Next set the right settings file and passwords as environment variables.
The passwords are the API client ids and secrets you got while registering your app at the providers website.
Virtualenvwrapper hook on activation:

    $ nano ~/.virtualenvs/moogle/bin/postactivate
    # Settings
    export DJANGO_SETTINGS_MODULE=moogle.settings.local

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

    $ nano ~/.virtualenvs/moogle/bin/predeactivate
    # Settings
    unset DJANGO_SETTINGS_MODULE

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

Reactivate the virtual environment:

    $ deactivate
    $ workon moogle

### 3.2. Using plain Virtualenv
    $ virtualenv ve

Next set the right settings file and passwords as environment variables.
The passwords are the API client ids and secrets you got while registering your app at the providers website (see README.md in the main folder).
Virtualenv hook on activation:

    $ nano ve/bin/activate
    # Settings
    export DJANGO_SETTINGS_MODULE=moogle.settings.local

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

    moogle/moogle/settings/vars.environment

This file will be IGNORED by Git, so it will be stored only in your local machine.
You might need it in case you accidentally remove your virtual environment and lose your passwords.


5. Install the requirements
---------------------------
    $ cd moogle
    $ pip install -r moogle/requirements/local.txt


6. Check the settings
---------------------
Check the settings file: `moogle/settings/local.py`


7. Create the db
----------------
    $ python manage.py syncdb --migrate


8. Import the fixtures
----------------------
    $ python manage.py loaddata tokens/fixtures/providers.json


9. Run the server
-----------------
    $ python manage.py runserver