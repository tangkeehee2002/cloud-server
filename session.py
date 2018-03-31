#!/usr/bin/env python3
"""Add sessions."""

from uuid import uuid4


class Session:
    """Session middleware for web server."""

    def __init__(self):
        """Initialize session dictionary."""
        self.SESSION = {}

    def __call__(self, request, response):
        """Return updated response object."""
        return self.session_middleware(request, response)

    def session_middleware(self, request, response):
        """Add sessions to the self.session."""
        try:
            sid = request["header"]["Cookie"].get("sid")
        except KeyError:
            sid = str(uuid4())
            response["header"]["Set-Cookie"] = "sid={}".format(sid)
            self.SESSION[sid] = {}
        return request, response

    def cookie_sid(self, request):
        try:
            sid = request["header"]["Cookie"].get("sid")
            return sid
        except KeyError:
            pass
        return False

    def add(self, request, content):
        """Add content to sid dictionary."""
        sid = self.cookie_sid(request)
        if sid:
            self.SESSION[sid].update(content)

    def get(self, request, key):
        """Get session data from self.SESSION."""
        sid = self.cookie_sid(request)
        if sid and self.SESSION[sid].get(key, False):
            return self.SESSION[sid][key]
        return None

    def pop(self, request):
        """Delete sid from self.session."""
        sid = self.cookie_sid(request)
        if sid:
            del self.SESSION[sid]
