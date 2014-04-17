MOOGLE PROJECT
==============

Imagine you want to search for that sushi restaurant someone recommended you last month: you type “sushi restaurant” in your smart phone and you get a tweet from a friend of yours talking about Tokyo Sushi. You also get a comment you wrote on Facebook, an SMS message you sent your girlfriend and a bookmark in your browser, all about the same restaurant. And imagine that you can do this with your smart phone, your laptop, tablet or smart TV. Something so basic yet so far from the reality...  
This is **Moogle - My Own Google**, the search engine for *private data*.

The project has 2 main components:

- **moogle**: a website which provides the main user interface.
- **magpie**: the core engine which crawls and index private data from service providers.

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
