The following fixture must be imported during the first install:
- providers.json
- users.json
- bearertokens.json

These features will create:
- Providers: Gmail, Drive, facebook, Dropbox, Twitter
- Users: admin, lev (inactive), paolo (inactive)
- BearerToken: an empty BearerToken w/ pk=50

Note: BearerTokens with pk <= 50 are considered to be test bearertokens.
This is the reason why the installation creates an empty BearerToken w/ pk = 50, so that any other
BearerToken will automatically have a pk > 50.

You can create a fixture file named:
test_user_lev_bearertokens.json
test_user_paolo_bearertokens.json
with the actual User and real BearerTokens.
But do NOT add it to VCS because, of course, BearerTokens are sensible info.
See test_user_lev_bearertokens.json.template.