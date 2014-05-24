import imaplib
import re

from tokens.models import Provider, BearerToken


class GmailSnooper:
    def __init__(self, user):
        self.user = user
        self.provider_name = Provider.NAME_GMAIL

    #def search(self, q):
    #    ##return [{'id': 'onegmail'}, {'id': 'twogmail'}, ]
    #
    #    imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
    #    #imap_conn.debug = 4  # Prints all the steps to stdout.
    #    auth_string = self._build_auth_string()
    #
    #    # TODO: IMAP must be enabled in the Gmail settings for the current user
    #    imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
    #    # TODO: Manage the expiration of Gmail token (see old project).
    #
    #    # Select the right folder is important cause the search will be restricted to that folder.
    #    # A select with no params will default to the inbox folder.
    #    #   imap_conn.select()  # default: 'INBOX'
    #    # We want to select the folder containing all mails.
    #    all_mail_folder = self._find_all_mail_folder(imap_conn.list())
    #    # Open a read-only connection cause we don;t need to send emails.
    #    imap_conn.select('"{}"'.format(all_mail_folder), readonly=True)
    #    #imap_conn.select('"[Gmail]/Chat"', readonly=True)
    #
    #    # Full text search like in Gmail webapp using the operator: X-GM-RAW.
    #    # Note: using the search criteria `in:all` the search will be anyway limited by the
    #    # selected folder.
    #    # `msgnums` is in the form: ['1656 1801']
    #    # `typ` is 'OK'
    #    typ, msgnums = imap_conn.search(None, '(X-GM-RAW "{}")'.format(q))
    #    # Like the `search` method but with UID.
    #    #typ, msgnums = imap_conn.uid('SEARCH', '(X-GM-RAW "{}")'.format(q))
    #    ids = msgnums[0].split()  # ids is now a list: ['1656', '1801'].
    #
    #    # Fetch resulting emails
    #    ids = ids[-10:]  # Considering only the most recent 10 emails.
    #    ids.reverse()  # Reverting the order so the most recent come first.
    #    emails = list()
    #    for id in ids:
    #        # Filtering fields to fetch only parts of the message is very useful cause it is
    #        # a way to optimize the performance of the process. But the protocol used to filter
    #        # the fields is very complicated.
    #        # Some filtering options:
    #        #  - (RFC822) -> the entire message.
    #        #  - (UID BODY[TEXT]) -> the UID and the text (UID is the unique msg identifier
    #        #    unique within the entire mailbox.
    #        #  - ((UID X-GM-MSGID X-GM-THRID) -> the UID and the identifiers which can be used
    #        #    to build a direct link to the message in gmail website.
    #        #  - (BODY[HEADER]) -> only the headers (from, to, subject, date, ...).
    #        #  - (ENVELOPE) -> ?.
    #        #  - (BODY[HEADER.FIELDS (SUBJECT FROM TO DATE)]) -> only subject, from, to, date.
    #        #  - (BODY[TEXT]<0.100>) -> only the first 100 bytes of the text.
    #        #  - (BODY.PEEK[1]<0.100> -> only the first 100 bytes of the first part (emails
    #        #    are divided in parts like plain, html, attachment, ...).
    #        #  - (BODY.PEEK[1.MIME]) -> only the mime of the first part.
    #        typ, data = imap_conn.fetch(id, "(UID X-GM-MSGID X-GM-THRID BODY[HEADER.FIELDS"
    #                                        " (SUBJECT FROM TO DATE)]"
    #                                        " BODY.PEEK[1.MIME] BODY.PEEK[1]<0.100>)")
    #        # Like method fetch but with uid.
    #        #typ, data = imap_conn.uid('FETCH', id, "(UID X-GM-MSGID X-GM-THRID"
    #        #                                       " BODY[HEADER.FIELDS (SUBJECT FROM TO DATE)]"
    #        #                                       " BODY.PEEK[1.MIME] BODY.PEEK[1]<0.100>)")
    #
    #        #print("{}\n\n".format(json.dumps(parse_fetch_response(data), indent=4)))
    #        emails.append(parse_fetch_response(data))
    #
    #    # Close connection
    #    imap_conn.close()
    #    imap_conn.logout()
    #
    #    return emails
    #
    #def _build_auth_string(self):
    #    email = ...  # Read it in the database.
    #    bearertoken = BearerToken.objects.get(user=self.user, provider__name=self.provider_name)
    #    return 'user={}\1auth=Bearer {}\1\1'.format(email, bearertoken.access_token)
    #
    #def _find_all_mail_folder(self, response):
    #    """
    #    Parse the response to a LIST command in order to get the All Mail folder name (which
    #    is different for different languages:
    #        "[Gmail]/All Mail" in English
    #        "[Gmail]/Tutti i messaggi" in Italian
    #    """
    #    # Response is a tuple made of 2 elements:
    #    #   - a string (useless)
    #    #   - a list of:
    #    #       - byte strings describing a folder
    #    #
    #    # There is no standard way to select the folder with all mail because this folder has
    #    # different names for different languages.
    #    # The only solution is to find the row with the text "\\All".
    #    # Also, do not assume that the start with "[Gmail]".  Sometimes it is "[Google Mail]"
    #    #
    #    # Example:
    #    #(
    #    #    'OK',
    #    #
    #    #    [
    #    #        b'(\\HasChildren) "/" "ALTRI ACCOUNT"',
    #    #        ... all labels ...
    #    #        b'(\\HasNoChildren) "/" "INBOX"',
    #    #        b'(\\HasNoChildren) "/" "Sent"',
    #    #        b'(\\Noselect \\HasChildren) "/" "[Gmail]"',
    #    #        b'(\\HasNoChildren \\Drafts) "/" "[Gmail]/Bozze"',
    #    #        b'(\\HasNoChildren) "/" "[Gmail]/Chat"',
    #    #        ...
    #    #        b'(\\HasNoChildren \\All) "/" "[Gmail]/Tutti i messaggi"'
    #    #    ]
    #    #)
    #    folders = []
    #    for i in response:
    #        if isinstance(i, list):
    #            folders = i
    #
    #    for folder in folders:
    #        folder = folder.decode("utf-8")  # cause folder is a byte string
    #        if '\\all' in folder.lower():
    #            # E.g. : '(\\HasNoChildren \\All) "/" "[Gmail]/Tutti i messaggi"'
    #            # Invert the string (str[::-1] and search the first occurence of "anything_but_double_quote"
    #            return re.match(r'"([^"]*)"', folder[::-1], re.I).group(1)[::-1]