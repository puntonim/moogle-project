The following fixture must be imported during the first install:
- providers.json

These features will create:
- Providers: Gmail, Drive, facebook, Dropbox, Twitter

Note: BearerTokens with pk <= 50 are considered to be test BearerTokens.
Keep in mind that BearerTokens are automatically imported from Moogle.

You can create a fixture w/ test BearerTokens using a file named like:
    `test_bearertokens.json`
with the real test BearerTokens (user pk <= 50).
But do NOT add it to VCS because, of course, BearerTokens are sensible info (.gitignore contains
the pattern `test_bearertokens.json`).
See `test_bearertokens.json.template`.