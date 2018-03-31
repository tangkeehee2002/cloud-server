#!/usr/bin/env python3
'''middleware helper function for server'''

import os
from uuid import uuid4

SESSIONS = {}

def session_middleware(request, response):
    """Add session ids to SESSION """
    browser_cookies = request["header"].get("Cookie", False)
    if browser_cookies:
        sid = request["header"]["Cookie"].get("sid", False)
    if sid:
        return request, response
    sid = str(uuid4())
    response["header"]["Set-Cookie"] = "sid={}".format(sid)
    SESSIONS[sid] = {}
    return request, response

def handle_sid(request, option):
    """Get session id from SESSIONS"""
    try:
        sid = request["header"]["Cookie"].get("sid")
    except KeyError as key:
        print("No {} in request header\n".format(key))
        return None
    if option == 'delete':
        del SESSIONS[sid]
    return sid

def logger(request, response):
    client_ip = request["header"]["Host"].split(":")[0]
    log_items = ("Date", "method", "path", "status")
    date, method, path, status = [response[i] for i in log_items]
    log = "{0} - - [{1}] \"{2} {3}\" {4}\n".format(client_ip, date, method, path, status)
    save_logs(log)
    return log, request, response

def save_logs(log, debug=False, filename="http_server.log"):
    if os.path.isfile(filename):
        with open(filename, mode="a") as log_data:
            log_data.write(log)
    if debug:
        print(log, end="")
