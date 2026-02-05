import re

def match_value(actual, expected):
    return actual == expected

def match_in_list(actual, expected_list):
    return actual in expected_list

def match_regex(actual, pattern):
    return bool(re.match(pattern, str(actual)))

def match_range(actual, range_tuple):
    return range_tuple[0] <= actual <= range_tuple[1]