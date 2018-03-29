#!/usr/bin/env python3
'''handles server side database'''

# import os
# import datetime
import crypt
from hmac import compare_digest as compare_hash
import redis


REDIS_OBJ = redis.StrictRedis("", port=6379)


def auth_login(login_details):
    username, passwd = login_details
    if  username is None or passwd is None:
        print("Enter login details")
        return False
    hashed_passwd = REDIS_OBJ.get(username)
    if compare_hash(hashed_passwd, crypt.crypt(passwd, hashed_passwd)):
        return True #get_homepage()
    print("Wrong password")
    return False

def save_signup(signup_details):
    signup_details[-1] = crypt.crypt(signup_details[-1]) # hashing passwd
    # passwd = signup_details[-1]
    # hashed_passwd = crypt.crypt(passwd)
    detail_names = ["fname", "lname", "email", "username", "passwd"]
    *_, username, hashed_passwd = signup_details
    user_id = REDIS_OBJ.incr("users")
    REDIS_OBJ.hmset(name="user:{}".format(user_id), mapping=dict(zip(detail_names, signup_details)))
    REDIS_OBJ.set(username, hashed_passwd)
    return True
