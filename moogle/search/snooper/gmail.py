import imaplib
import re
import base64

from tokens.models import Provider, BearerToken


class GmailSnooper:
    def __init__(self, user):
        self.user = user
        self.provider_name = Provider.NAME_GMAIL
        self.email_address = 'johndoe@gmail.com'  # TODO: Read it in the database.

    def search(self, q):
        imap = self._connect()

        # Select the right folder is important cause the search will be restricted to that folder.
        # A select with no params will default to the inbox folder.
        #   imap_conn.select()  # Default: 'INBOX'.
        # We want to select the folder containing all mails.
        all_mail_folder = FetchedEmailParser.find_all_mail_folder(imap.list())
        # Open a read-only connection cause we don;t need to send emails.
        imap.select('"{}"'.format(all_mail_folder), readonly=True)
        #imap_conn.select('"[Gmail]/Chat"', readonly=True)

        # Full text search like in Gmail website using the operator: X-GM-RAW.
        # Note: using the search criteria `in:all` the search will be anyway limited to the
        # selected folder.
        typ, msgnums = imap.search(None, '(X-GM-RAW "{}")'.format(q))  # `msgnums` is in the form:
                                                                       # ['1656 1801'].
                                                                       # `typ` is 'OK'.
        # Like the `search` method but with UID.
        #typ, msgnums = imap_conn.uid('SEARCH', '(X-GM-RAW "{}")'.format(q))
        ids = msgnums[0].split()  # `ids` is a list: ['1656', '1801'].

        # Fetch resulting emails.
        ids = ids[-10:]  # Considering only the most recent 10 emails.
        ids.reverse()  # Reverting the order so the most recent come first.
        emails = list()
        for id in ids:
            # Filtering fields to fetch only parts of the message is very useful cause it is
            # a way to optimize the performance of the process. But the protocol used to filter
            # the fields is very complicated.
            # Some filtering options:
            #  - (RFC822) -> the entire message.
            #  - (UID BODY[TEXT]) -> the UID and the text (UID is the unique msg identifier
            #    unique within the entire mailbox.
            #  - ((UID X-GM-MSGID X-GM-THRID) -> the UID and the identifiers which can be used
            #    to build a direct link to the message in gmail website.
            #  - (BODY[HEADER]) -> only the headers (from, to, subject, date, ...).
            #  - (ENVELOPE) -> ?.
            #  - (BODY[HEADER.FIELDS (SUBJECT FROM TO DATE)]) -> only subject, from, to, date.
            #  - (BODY[TEXT]<0.100>) -> only the first 100 bytes of the text.
            #  - (BODY.PEEK[1]<0.100> -> only the first 100 bytes of the first part (emails
            #    are divided in parts like plain, html, attachment, ...).
            #  - (BODY.PEEK[1.MIME]) -> only the mime of the first part.
            typ, data = imap.fetch(id, "(UID X-GM-MSGID X-GM-THRID BODY[HEADER.FIELDS"
                                            " (SUBJECT FROM TO DATE)]"
                                            " BODY.PEEK[1.MIME] BODY.PEEK[1]<0.100>)")
            # Like method fetch but with uid.
            #typ, data = imap_conn.uid('FETCH', id, "(UID X-GM-MSGID X-GM-THRID"
            #                                       " BODY[HEADER.FIELDS (SUBJECT FROM TO DATE)]"
            #                                       " BODY.PEEK[1.MIME] BODY.PEEK[1]<0.100>)")

            # Parse and add the fetched email.
            parser = FetchedEmailParser(data, self.email_address)
            emails.append(parser.parse())

        # Close connection.
        self._disconnect(imap)

        return emails

    def _build_auth_string(self):
        """
        Build the auth string required for Gmail IMAP.
        """
        bearertoken = BearerToken.objects.get(user=self.user, provider__name=self.provider_name)
        # TODO: it shouldn't be `bearertoken.access_token['access_token']`, but `bearertoken.access_token`
        return 'user={}\1auth=Bearer {}\1\1'.format(self.email_address, bearertoken.access_token['access_token'])

    def _connect(self):
        """
        Open a IMAP connection to Gmail.
        """
        def do_connect(connection):
            connection.authenticate('XOAUTH2', lambda x: auth_string)

        connection = imaplib.IMAP4_SSL('imap.gmail.com')
        #connection.debug = 4  # Prints all the steps to stdout.
        auth_string = self._build_auth_string()

        # TODO: IMAP must be enabled in the Gmail settings for the current user
        try:
            do_connect(connection)
        except imaplib.IMAP4.error as e:
            # TODO: Manage the expiration of Gmail token (see old project).
            if 'invalid credentials' in str(e).lower():
                print('YOU HAVE TO REFRESH THE TOKEN')
                # TODO: first refresh token
                # TODO: then: do_connect(connection)
                raise
            else:
                raise
        return connection

    def _disconnect(self, connection):
        """
        CLose a IMAP connection to Gmail.
        """
        connection.close()
        connection.logout()


class FetchedEmailParser:
    """
    Parse and email as fetched from Gmail IMAP and create a dictionary in the following form:
    {
        'from': '=?utf-8?Q?Jeffrey?= <cinema.acephale@gmail.com>',
        'to': '=?utf-8?Q?johndoe=40gmail.com?= <johndoe@gmail.com>',
        'date': 'Wed, 19 Mar 2014 00:20:55 +0000',
        'subject': '=?utf-8?Q?Upcoming=20cinema=3A=20The=20Ascent=2C=20The=20Producers=2C=20
                   'Marienbad=2C=20Dog=20Day=20Afternoon?=',
        'text': 'Jeffrey underground cinemas All films in English or with English subtitles',
        'thread_link': 'http://mail.google.com/mail?account_id=johndoe@gmail.com&message_id='
                       '144d7b6c4392be36&view=conv&extsrc=atom',
        'message_link': 'http://mail.google.com/mail?account_id=johndoe@gmail.com&message_id='
                        '144d7b6c4392be36&view=conv&extsrc=atom',
        'content-transfer-encoding': 'quoted-printable',
        'content-type': 'text/plain; charset="utf-8"; format="fixed"',
    }
    """
    def __init__(self, response, email_address):
        self.response = response
        self.email = dict()
        self.email_address = email_address

    def parse(self):
        """
        Parse the response to a FETCH command. The response is the representation of a single
        email message. We parse this response a create a dictionary to represent the email msg.

        `self.response` is a list made of 3 main parts:
          - PART 1: a tuple made of:
               - a byte string which is a sort of key of the 1st part of the response.
               - a byte string which is a sort of content of the 1st part of the response.
          - PART 2: a tuple made of:
               - a byte string which is a sort of key of the 2nd part of the response.
               - a byte string which is a sort of content of the 2nd part of the response.
          - PART 3: a tuple made of:
               - a byte string which is a sort of key of the 3rd part of the response.
               - a byte string which is a sort of content of the 3rd part of the response.
          - a byte string (a nonsense).

        Example of `self.response`:
        [
            # PART 1
            (b' 24294 (X-GM-THRID 1447735411271508216 X-GM-MSGID 1447735411271508216 UID 110780
              BODY[HEADER.FIELDS (SUBJECT FROM TO DATE)] {172}',
             b'Date: Sat, 22 Dec 2007 06:28:42 -0800\r\nFrom: "Il team di Gmail"
               <mail-noreply@google.com>\r\nTo: "John Doe" <johndoe@gmail.com>\r\nSubject:
               =?ISO-8859-1?Q?Gmail_=E8_diverso._Queste_sono_le_informazioni_essen?=\r\n
               =?ISO-8859-1?Q?ziali_che_devi_conoscere_prima_di_poter_procedere.?=\r\n\r\n'),

            # PART 2
            (b' BODY[1]<0> {100}',
             b'To spice up your inbox with colors and themes, check out the Themes tab under
               Settings'),

            # PART 3
            (b' BODY[1.MIME] {122}',
             b'Content-Type: text/plain; charset=ISO-8859-1\r\nContent-Transfer-Encoding:
               quoted-printable\r\nContent-Disposition: inline\r\n\r\n'),

             b')'
        ]
        """
        for el in self.response:
            if not isinstance(el, tuple):
                continue  # We found the element: b')' (which is a byte).
            key = el[0].decode("utf-8")
            value = el[1].decode("utf-8")

            if 'HEADER' in key.upper():
                self._parse_part1(key, value)

            elif 'MIME' in key.upper():
                self._parse_part3(key, value)

            else:
                self._parse_part2(key, value)

        # Fix text, like decoding base64-encoded text.
        self._fix_text_()

        return self.email

    def _parse_part1(self, key, value):
        """
        Parse the part1 of a response.
        Part1 is made of `key` and `value`, e.g.:
            ID of message valid only in the current folder
                 ^               X-GM-THRID of message: to use to build a direct web link
                 |               to the conversation
                 |                      ^                   X-GM-MSGID of message: to use to build
                 |                      |                   a direct web link to the email
                 |                      |                                ^
                 |                      |                                |    UID of message (unique
                 |                      |                                |    identifier among the
                 |                      |                                |    entire mailbox)
                 |                      |                                |                ^
                 |                      |                                |                |
        key = ' 24294 (X-GM-THRID 1447735411271508216 X-GM-MSGID 1447735411271508216 UID 110780
               BODY[HEADER.FIELDS (SUBJECT FROM TO DATE)] {172}'

        value = 'Date: Sat, 22 Dec 2007 06:28:42 -0800\r\n
                 From: "Il team di Gmail" <mail-noreply@google.com>\r\n
                 To: "John Doe" <johndoe@gmail.com>\r\n
                 Subject: =?ISO-8859-1?Q?Gmail_=E8_diverso._Queste_sono_le_informazioni_essen?=\r\n
                 =?ISO-8859-1?Q?ziali_che_devi_conoscere_prima_di_poter_procedere.?=\r\n
                 \r\n'
        """
        # Get X-GM-THRID from the key, convert to hex and create the actual link to the
        # thread in Gmail website.
        try:
            thrid = re.search(r'X-GM-THRID (\S*)', key, re.I)
            thrid = thrid.group().upper().replace('X-GM-THRID', '').strip()
            thrid = hex(int(thrid))[2:]
            self.email['thread_link'] = ('http://mail.google.com/mail?account_id={}&message_id={}'
                '&view=conv&extsrc=atom'.format(self.email_address, thrid))
        except Exception:
            # No problem if we cannot parse the X-GM-THRID (it wont be shown in the template).
            pass

        # Get X-GM-MSGID from the key, convert to hex and create the actual link to the
        # message in Gmail website.
        try:
            msgid = re.search(r'X-GM-MSGID (\S*)', key, re.I)
            msgid = msgid.group().upper().replace('X-GM-MSGID', '').strip()
            msgid = hex(int(msgid))[2:]
            self.email['message_link'] = ('http://mail.google.com/mail?account_id={}&message_id={}'
                '&view=conv&extsrc=atom'.format(self.email_address, msgid))
        except Exception:
            # No problem if we cannot parse the X-GM-MSGID (it wont be shown in the template).
            pass

        # Get the email headers.
        for line in value.splitlines():
            if 'from: ' in line.lower():
                self.email['from'] = line[6:].replace('\"', '')
            elif 'to: ' in line.lower():
                self.email['to'] = line[4:].replace('\"', '')
            elif 'subject: ' in line.lower():
                self.email['subject'] = line[9:]
            elif 'date: ' in line.lower():
                self.email['date'] = line[6:]

    def _parse_part2(self, key, value):
        """
        Parse the part2 of a response.
        Part2 is made of `key` and `value`, e.g.:
        key = ' BODY[1]<0> {100}'
        value = 'To spice up your inbox with colors and themes, check out the Themes tab under
                 Settings'
        """
        self.email['text'] = value

    def _parse_part3(self, key, value):
        """
        Parse the part3 of a response.
        Part3 is made of `key` and `value`, e.g.:
        key = ' BODY[1.MIME] {122}'
        value = 'Content-Type: text/plain; charset=ISO-8859-1\r\n
                 Content-Transfer-Encoding: quoted-printable\r\n
                 Content-Disposition: inline\r\n
                 \r\n'
        """
        for line in value.splitlines():
            if 'content-type: ' in line.lower():
                self.email['content-type'] = line[14:]
            elif 'content-transfer-encoding: ' in line.lower():
                self.email['content-transfer-encoding'] = line[27:]

    def _fix_text_(self):
        # When the text is encoded with base64.
        if 'base64' in self.email.get('content-transfer-encoding', '').lower():
            # Decode the first 98 chars w/ base 64.
            # Why 98? Cause the length must be a multiple of something... 100 doesn't always work.
            self.email['text'] = base64.b64decode(self.email['text'][:98]).decode("utf-8")

        # When the text is in plain-text.
        if 'plain' in self.email.get('content-type', '').lower():
            self.email['text'] = self.email['text'].replace('\r\n', ' ').strip()
            self.email['text'] = self.email['text'].replace('\n', ' ').strip()
            self.email['text'] = self.email['text'].replace('\r', ' ').strip()

        # When the text is in HTML.
        #if 'html' in email['content-type'].lower():
        #    self.email['text'] = TODO try to decode the html

    @staticmethod
    def find_all_mail_folder(response):
        """
        Parse the response to a LIST command in order to get the "All Mail" folder name (which
        is different for different languages:
            "[Gmail]/All Mail" in English.
            "[Gmail]/Tutti i messaggi" in Italian.

        Parameters:
        response -- a tuple of 2 elements:
            - a string like: 'OK'
            - a list of byte-strings describing a folder.
        Example of `response`:
        ('OK',
         [
            b'(\\HasChildren) "/" "ALTRI ACCOUNT"',
            ... all labels ...
            b'(\\HasNoChildren) "/" "INBOX"',
            b'(\\HasNoChildren) "/" "Sent"',
            b'(\\Noselect \\HasChildren) "/" "[Gmail]"',
            b'(\\HasNoChildren \\Drafts) "/" "[Gmail]/Bozze"',
            b'(\\HasNoChildren) "/" "[Gmail]/Chat"',
            ...
            b'(\\HasNoChildren \\All) "/" "[Gmail]/Tutti i messaggi"'
         ])
        """
        # There is no standard way to select the folder with all mail because this folder has
        # different names for different languages.
        # The only solution is to find the row with the text "\\All".
        # Also, do not assume that the start with "[Gmail]".  Sometimes it is "[Google Mail]"
        folders = []
        for i in response:
            if isinstance(i, list):
                folders = i

        for folder in folders:
            folder = folder.decode("utf-8")  # Cause folder is a byte string.
            if '\\all' in folder.lower():
                # E.g. : '(\\HasNoChildren \\All) "/" "[Gmail]/Tutti i messaggi"'.
                # Invert the string (str[::-1] and search the first occurrence of
                # "anything_but_double_quote".
                return re.match(r'"([^"]*)"', folder[::-1], re.I).group(1)[::-1]