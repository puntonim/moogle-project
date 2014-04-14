MOOGLE PROJECT
==============

The search engine for *private data*.

The project has 2 main components:

- **moogle**: a website powered by Django where user can search their private data.
- **magpie**: a web crawler to harvest and index private data.

Follow the steps written in the README.md files in `magpie` and `moogle` folder in order to create a *local development* copy.
**NOTE** The project is still in its early stages.


Foreword
--------
Register your own app at the providers websites and get an API client id and a secret.

- Google
    - App management URL: https://cloud.google.com/console/project
    - Permissions: Drive API.
    - Note: Gmail and Drive use the same key.
- Facebook
    - App management URL: https://developers.facebook.com/apps
    - Options to enable: Client OAuth Login, Embedded browser OAuth Login.
    - Redirect URI: http://127.0.0.1:8000/tokens/add/facebook/callback
- Twitter
    - App management URL: https://dev.twitter.com/apps
    - Access level: Read-only.
    - Callback URL: http://127.0.0.1:8000/tokens/add/twitter/callback
- Dropbox
    - App management URL: https://www.dropbox.com/developers/apps
    - Permission type: File type.
    - Allowed file types: documents, eBooks, text files.
    - Redirect URI: http://127.0.0.1:8000/tokens/add/dropbox/callback