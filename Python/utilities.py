"""
Title: String Trimming Utilities
Author: [Your Name]
Date: [Date]
Description: Provides functions to trim strings based on specified delimiters.
Version: 1.0
Usage: Import this module to use the string trimming functions.
"""

def string_trim_left_to(string, to):
    """
    Trims the string from the left up to the last occurrence of 'to'.

    Args:
    string (str): The string to be trimmed.
    to (str): The delimiter indicating where to trim.

    Returns:
    str: The trimmed string.
    """
    return string.rsplit(to, 1)[-1]
    
def string_trim_right_from(string, from_):
    """
    Trims the string from the right starting from the first occurrence of 'from_'.

    Args:
    string (str): The string to be trimmed.
    from_ (str): The delimiter indicating where to trim.

    Returns:
    str: The trimmed string.
    """
    return string.split(from_, 1)[0]

