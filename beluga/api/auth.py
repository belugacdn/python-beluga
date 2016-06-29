import urlparse
import base64
import datetime
import hashlib
import hmac

from requests.auth import AuthBase


class BelugaAPIAuth(AuthBase):

    def __init__(self, id=None, secret=None, username=None, password=None):
        if username:
            self.username = username
        else:
            self.username = None

        if password:
            self.password = password
        else:
            self.password = None

        if id:
            self.id = id
        else:
            self.id = None

        if secret:
            self.secret = secret
        else:
            self.secret = None

    def __call__(self, request):
        if self.id and self.secret:
            return self.token_sign(request)
        elif self.username and self.password:
            return self.http_basic(request)
        else:
            raise Exception(
                "id and secret or username and password are required")

    def http_basic(self, request):
        request.headers['Authorization'] = 'Basic %s' % base64.b64encode(
            "%s:%s" % (self.username, self.password))
        return request

    def token_sign(self, request):
        urlparsed = urlparse.urlparse(request.url)
        if urlparsed.params:
            path_qs = '%s?%s' % (urlparsed.path, urlparsed.params)
        else:
            path_qs = urlparsed.path

        date = datetime.datetime.utcnow().isoformat("T") + "Z"
        request.headers['Date'] = date
        signstring = '%s:%s:%s' % (request.method, path_qs, date)

        if request.method in ['POST', 'PUT']:
            bodyhash = hashlib.sha512(request.body).hexdigest()
            signstring = "%s:%s" % (signstring, bodyhash)

        signhmac = hmac.new(
            self.secret, signstring, hashlib.sha512).hexdigest()
        request.headers['Authorization'] = 'Token %s %s' % (self.id, signhmac)

        return request
