# petl_ldap3
Provides an LdapView class and a function fromldap that can be used to extract data from an ldap directory and turn it into a petl table.

fromldap requires a valid ldap3.Connection to be passed in.
fromldap also requires a base ou to start serching and search query in RFC2254 format. (https://www.ietf.org/rfc/rfc2254.txt)
