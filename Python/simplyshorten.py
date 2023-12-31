import requests
import random
import string

"""
Title: Simply Shorten
Author: WookedWare
Description: Provides functions to trim interact with Simply Shorten's api
Version: 1.0
"""

def domain_format(domain, username=None, password=None):
    """
    Formats the domain with optional username and password.

    :param domain: The domain URL.
    :param username: Optional username for authentication.
    :param password: Optional password for authentication.
    :return: Formatted domain URL.

    Example:
        domain_format("https://ur.l", "admin", "admin") -> "https://admin:admin@ur.l"
    """
    protocol = "http"
    if domain.startswith("http://"):
        domain = domain[7:]
    elif domain.startswith("https://"):
        domain = domain[8:]
        protocol = "https"

    if username and password:
        return f"{protocol}://{username}:{password}@{domain}"
    else:
        return f"{protocol}://{domain}"


def links_list(domain):
    """
    Lists all short links for the given domain.

    :param domain: The domain URL.
    :return: List of short links.

    Example:
        links_list("http://admin:admin@ur.l") -> [{"short": "abc", "long": "http://example.com"}, ...]
    """
    response = requests.get(f"{domain}/api/all")
    urls = response.text.split("\n")
    links = [{"short": url.split(',')[0], "long": url.split(',')[1]} for url in urls if url]
    return links


def link_create(domain, long, short=None):
    """
    Creates a short link for the given long URL.

    :param domain: The domain URL.
    :param long: The long URL to shorten.
    :param short: Optional custom short URL.
    :return: Short URL or None if it already exists.

    Example:
        link_create("http://admin:admin@ur.l", "http://example.com", "exmpl") -> "exmpl"
    """
    if short is None:
        attempts = 0
        length = 3
        while True:
            short = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
            if not link_check_short_exists(domain, short):
                break
            attempts += 1
            if attempts == 20:
                length += 1
                attempts = 0

    if link_check_short_exists(domain, short):
        return None

    if not long.startswith("http://") and not long.startswith("https://"):
        long = "http://" + long

    response = requests.post(f"{domain}/api/new", data=f"{long};{short}")
    return short


def link_delete_short(domain, short_url):
    """
    Deletes a short link by its short URL.

    :param domain: The domain URL.
    :param short_url: The short URL to delete.
    :return: True if deleted, False otherwise.

    Example:
        link_delete_short("http://admin:admin@ur.l", "exmpl") -> True
    """
    response = requests.delete(f"{domain}/api/{short_url}")
    if response.status_code == 200:
        return True
    else:
        return False


def link_delete_long(domain, long):
    """
    Deletes all short links for the given long URL.

    :param domain: The domain URL.
    :param long: The long URL to delete.
    :return: True if any links deleted, False otherwise.

    Example:
        link_delete_long("http://admin:admin@ur.l", "http://example.com") -> True
    """
    normalized_long = long.replace("http://", "").replace("https://", "").replace("www.", "").split('/')[0]
    deleted_any = False
    while True:
        short_url = link_get_short(domain, normalized_long)
        if short_url:
            if link_delete_short(domain, short_url):
                deleted_any = True
            else:
                break
        else:
            break
    return deleted_any


def links_delete_all(domain):
    """
    Deletes all short links for the given domain.

    :param domain: The domain URL.
    :return: True if any links deleted, False otherwise.

    Example:
        links_delete_all("http://admin:admin@ur.l") -> True
    """
    links = links_list(domain)
    deleted_any = False
    for link in links:
        success = link_delete_short(domain, link["short"])
        if success:
            deleted_any = True
    return deleted_any


def link_get_short(domain, long):
    """
    Gets the short URL for the given long URL.

    :param domain: The domain URL.
    :param long: The long URL to find.
    :return: Short URL or None if not found.

    Example:
        link_get_short("http://admin:admin@ur.l", "http://example.com") -> "exmpl"
    """
    normalized_long = long.replace("http://", "").replace("https://", "").replace("www.", "").split('/')[0]
    links = links_list(domain)
    for link in links:
        normalized_link_long = \
        link['long'].replace("http://", "").replace("https://", "").replace("www.", "").split('/')[0]
        if normalized_link_long == normalized_long:
            return link['short']
    return None


def link_get_long(domain, short):
    """
    Gets the long URL for the given short URL.

    :param domain: The domain URL.
    :param short: The short URL to find.
    :return: Long URL or None if not found.

    Example:
        link_get_long("http://admin:admin@ur.l", "exmpl") -> "http://example.com"
    """
    links = links_list(domain)
    for link in links:
        if link['short'] == short:
            return link['long']
    return None


def link_check_short_exists(domain, short):
    """
    Checks if a short URL exists.

    :param domain: The domain URL.
    :param short: The short URL to check.
    :return: True if exists, False otherwise.

    Example:
        link_check_short_exists("http://admin:admin@ur.l", "exmpl") -> True
    """
    long_link = link_get_long(domain, short)
    if long_link:
        return True
    else:
        return False


def link_update(domain, short, long):
    """
    Updates a short link with a new long URL.

    :param domain: The domain URL.
    :param short: The short URL to update.
    :param long: The new long URL.
    :return: Updated short URL or None if not found.

    Example:
        link_update("http://admin:admin@ur.l", "exmpl", "http://newexample.com") -> "exmpl"
    """
    link_delete_short(domain, short)
    return link_create(domain, long, short)
