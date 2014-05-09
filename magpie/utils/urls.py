import re


def remove_urls(text):
    """
    Remove all URLs from a `text`. Return clean text and URLs list.

    Parameters:
    text -- the text to be cleaned.
    """
    # Regex to identify URLs
    regex = ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|'
             '(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    urls = re.findall(regex, text)

    for u in urls:
        text = text.replace(u, '')  # Replace all occurrences.

    return text.strip(), urls