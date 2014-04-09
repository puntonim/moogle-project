Moogle
======

The search engine for *private data*.

The project has 2 main components:

- **moogle**: a website powered by Django where user can search their private data.
- **magpie**: a web crawler to harvest and index private data.

Follow the steps in order to create a *local development* copy.

Foreword
--------
Register your own app at the providers websites and get an API client id and a secret.

- Google
https://cloud.google.com/console/project
Permissions: Drive API.
Gmail and Drive use the same key.
- Facebook
https://developers.facebook.com/apps
Enable: Client OAuth Login, Embedded browser OAuth Login.
Redirect URI: http://127.0.0.1:8000/tokens/add/facebook/callback
- Twitter
https://dev.twitter.com/apps
Access level: Read-only.
Callback URL: http://127.0.0.1:8000/tokens/add/twitter/callback
- Dropbox
https://www.dropbox.com/developers/apps
Permission type: File type.
Allowed file types: documents, eBooks, text files.
Redirect URI: http://127.0.0.1:8000/tokens/add/dropbox/callback



MOOGLE (WEBSITE)
----------------
### 1. Create a project folder in your workspace
    $ mkdir moogle-project
    $ cd moogle-project
We will refer to this folder as *repository root*.


### 2. Clone the reposiotry
    $ git clone https://github.com/nimiq/moogle-project.git .


### 3. Create a virtual environment
#### 3.1. Using Virtualenvwrapper
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

#### 3.2. Using plain Virtualenv
    $ virtualenv ve

Next set the right settings file and passwords as environment variables.
The passwords are the API client ids and secrets you got while registering your app at the providers website.
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


### 4. Optional: local copy of environment variables (passwords)
Optionally make a copy of the environment variables (the passwords) in the file:

    icecreamshop/icecreamshop/settings/vars.environment

This file will be IGNORED by Git, so it will be stored only in your local machine.
You might need it in case you accidentally remove your virtual environment and lose your passwords.


### 5. Install the requirements
    $ cd moogle
    $ pip install -r moogle/requirements/local.txt

### 6. Check the settings
Check the settings file: `moogle/settings/local.py`

### 7. Create the db
    $ python manage.py syncdb --migrate

### 8. Import the fixtures
    $ python manage.py loaddata tokens/fixtures/providers.json

### 9. Run the server
    $ python manage.py runserver


















MAGPIE
------

### 1. Create a project folder in your workspace
    $ mkdir moogle-project
    $ cd moogle-project
We will refer to this folder as *repository root*.


### 2. Clone the reposiotry
    $ git clone https://github.com/nimiq/moogle-project.git .


### 3. Create a virtual environment
#### 3.1. Using Virtualenvwrapper
    $ mkvirtualenv magpie

Next set the right settings file and passwords as environment variables.
The passwords are the API client ids and secrets you got while registering your app at the providers website.
Virtualenvwrapper hook on activation:

    $ nano ~/.virtualenvs/magpie/bin/postactivate
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
    $ workon moogle

#### 3.2. Using plain Virtualenv
    $ virtualenv ve

Next set the right settings file and passwords as environment variables.
The passwords are the API client ids and secrets you got while registering your app at the providers website.
Virtualenv hook on activation (user your own *path* for `PYTHONPATH`):

    $ nano ve/bin/activate
    # PYTHONPATH
    export PYTHONPATH="/Users/my_user/workspace/moogle-project/magpie"

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


### 4. Optional: local copy of environment variables (passwords)
Optionally make a copy of the environment variables (the passwords) in the file:

    icecreamshop/icecreamshop/settings/vars.environment

This file will be IGNORED by Git, so it will be stored only in your local machine.
You might need it in case you accidentally remove your virtual environment and lose your passwords.


### 5. Install the requirements
    $ cd magpie
    $ pip install -r magpie/requirements.txt


TODO: complete this