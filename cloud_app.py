#!/usr/bin/env python3
'''handles server side database'''

import os
# import datetime
import crypt
from hmac import compare_digest as compare_hash
from shutil import copy
import redis
import server

REDIS_OBJ = redis.StrictRedis("", port=6379)


def auth_login(login_details):
    if not login_details.pop("op") == 'login':
        return False
    if login_details.get("user", False) and login_details.get("password", False):
        username, passwd = login_details["user"], login_details["password"]
    hashed_passwd = REDIS_OBJ.get(username)
    if compare_hash(hashed_passwd, crypt.crypt(passwd, hashed_passwd)):
        return (username, True) #get_homepage()
    print("Wrong password")
    return False

def save_signup(signup_details):
    if not signup_details.pop("op") == 'signup':
        return False
    if len(signup_details) < 6:
        print("Missing details")
        return False
    fname, lname, email, username, passwd = list(signup_details.values())
    if REDIS_OBJ.get(username):
        print("username already taken")
        # check already registered email too
    if len(passwd) < 8:
        print("password should have minimum of 8 characters")
        return False

    hashed_passwd = crypt.crypt(passwd)
    detail_names = [fname, lname, email, username, hashed_passwd]
    user_id = REDIS_OBJ.incr("users")
    REDIS_OBJ.hmset(name="user:{}".format(user_id), mapping=dict(zip(detail_names, signup_details)))
    REDIS_OBJ.hmset(name=username, mapping=dict(zip(detail_names, signup_details)))
    REDIS_OBJ.set(username, hashed_passwd)
    # REDIS_OBJ.set(username, userid)

    os.mkdir("./users_cloud/{}".format(username))
    src_file = os.path.abspath("./static/login/files.html")
    dst_file = os.path.abspath("./users_cloud/{}/files.html".format(username))
    copy(src_file, dst_file)
    return (username, user_id) # return login page again

def post_handling():
    server.handle_post_methods(body="parsed_request_body", op_type="login", function=auth_login)
    server.handle_post_methods(body="parsed_request_body", op_type="signup", function=save_signup)

def add_route():
    pass
