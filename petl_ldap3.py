# -*- coding: utf-8 -*-
"""A PETL LDAPView class. Need this until I can get my changes included in the main PETL package."""
from __future__ import absolute_import, print_function, division


# standard library dependencies
import logging

# internal dependencies
from petl.util.base import Table

# external dependencies
import ldap3


logger = logging.getLogger(__name__)
debug = logger.debug
warning = logger.warning


def fromldap(connection, base_ou, query, attributes=[], scope=ldap3.SUBTREE, page_size=500, defaults=None, joiner=';'):
    return LdapView(connection, base_ou, query, attributes, scope, page_size, defaults, joiner)


class LdapView(Table):
    def __init__(self, connection, base_ou, query, attributes, scope, page_size, defaults=None, joiner=';'):
        self.connection = connection
        self.base_ou = base_ou
        self.query = query
        self.attributes = attributes
        self.scope = scope
        self.page_size = page_size
        self.defaults = defaults
        self.joiner = joiner

    def __iter__(self):
        return _iter_ldap_query(self.connection, self.base_ou, self.query, self.attributes, self.scope, self.page_size, self.defaults, self.joiner)


def _iter_ldap_query(connection, base_ou, query, attributes, scope, page_size, defaults=None, joiner=';'):
    connection.bind()
    connection.search(search_base=base_ou, search_filter=query, search_scope=scope, attributes=attributes, paged_size=page_size, paged_cookie=None)
    logger.debug('Connection.search.response is: {}'.format(connection.response))
    # Yield the headers, PETL expects that first.
    yield attributes
    while True:
        results = connection.response
        for result in results:
            row = []
            for attribute in attributes:                
                try:
                    value = result['attributes'][attribute]
                except KeyError as ke:
                    if defaults is not None:
                        try:
                            value = defaults[attribute]
                        except KeyError as ike:
                            logger.exception(f'No value returned for attribute: {attribute} and no default could be found.')
                            raise ke
                else:
                    # What sort of value did we get?
                    if isinstance(value, (list, tuple)):
                        if len(value) == 1:
                            # Single value
                            row.append(value[0])
                        elif len(value) > 1:
                            # Multiple values, convert to a single value for petl.
                            row.append(joiner.join(value))
                        # Do i need to deal with an empty list?
                    else:
                        row.append(value)
            yield row
        cookie = connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        if cookie:
            connection.search(search_base=base_ou, search_filter=query, search_scope=scope, attributes=attributes, paged_size=page_size, paged_cookie=cookie)
        else:
            break
    connection.unbind()
