#!/usr/bin/env python3
'''handles server side database'''

import os
# from subprocess import (Popen, PIPE)
# import datetime
import crypt
from hmac import compare_digest as compare_hash
from shutil import copytree
from time import ctime
from jinja2 import Template
import redis
import server


# REDIS_OBJ = redis.StrictRedis("", port=6379)
REDIS_OBJ = redis.StrictRedis()
CWD = os.getcwd()


def handle_login(request, response, login_details):
    # print("handle_login")
    username, passwd = login_details["user"], login_details["password"]
    hashed_passwd = REDIS_OBJ.get(username)
    if hashed_passwd:
        hashed_passwd = hashed_passwd.decode()
        if compare_hash(hashed_passwd, crypt.crypt(passwd, hashed_passwd)):
            redir_path = "user/{}/home.html".format(username).encode()
            # print(redir_path)

            # server.redirect(request, response, redirected_path, 307)
            return read_html("static/home.html").replace(b"{redirect}", redir_path)
    return read_html("static/failed_login.html").replace(b'{reason}', b'wrong credentials')

    # fail_reason = {'reason': 'wrong credentials'}

def handle_signup(request, response, signup_details):
    # print("handle_signup")
    validity_status = signup_validity(signup_details)
    if not validity_status[0]:
        res_page = read_html('static/failed_signup.html')
        return res_page.replace(b"{reason}", validity_status[1])
    username, password = signup_details["username"], signup_details["password"]
    signup_details["password"] = crypt.crypt(password)
    # detail_names = [fname, lname, email, username, hashed_passwd]
    user_id = REDIS_OBJ.incr("users")
    REDIS_OBJ.hmset(name="user:{}".format(user_id), mapping=signup_details)
    REDIS_OBJ.hmset(name=username, mapping=signup_details)
    # REDIS_OBJ.hmset(name="user:{}".format(user_id), dict(zip(detail_names, signup_details)))
    # REDIS_OBJ.hmset(name=username, mapping=dict(zip(detail_names, signup_details)))
    REDIS_OBJ.set(username, signup_details["password"])
    REDIS_OBJ.save()
    # REDIS_OBJ.set(username, userid)
    src = os.path.abspath("static/login")
    dst = os.path.abspath("static/user/{}".format(username))
    if not os.path.exists(dst):
        copytree(src, dst)
    os.mkdir("{}/uploads".format(dst))
    # redirected_path = "user/{}/home.html".format(username)
    # server.redirect(request, response, redirected_path, 307)
    return read_html("static/user/{}/index.html".format(username))# return login page again
#

def read_html(html):
    # print("read_html")
    html_abspath = os.path.abspath(html)
    with open(html_abspath, "rb") as page:
        html_bytes = page.read()
        return html_bytes


def signup_validity(signup_details):
    # print("signup_validity")
    if '' in [i.strip() for i in signup_details.values()]:
        return False, b"Empty spaces are not valid"
    if len(signup_details) < 6:
        return False, b"Missing details"
    username, passwd = signup_details["username"], signup_details["password"]
    if REDIS_OBJ.get(username):
        return False, b"username already taken"
    if REDIS_OBJ.get("{}.email".format(username)):
        return False, b"Already registered with this email"
    if len(passwd) < 8:
        return False, b"password should have minimum of 8 characters"
    return True, b"valid"

def save_uploads(request, response, parsed_request_body):
    # parsed_request_body = request["body"]
    user = request["header"]["Referer"].split("/")[-2]
    # user, _ = post_from
    user_dir = 'static/user/{}/'.format(user)
    upload_dir = "{}uploads/".format(user_dir)
    for file in parsed_request_body:
        filename = os.path.abspath(upload_dir + file)
        with open(filename, "wb") as fname:
            fname.write(parsed_request_body[file]["body"])

        # server.redirect(request, response, redirected_path, 307)
    user_files = [upload_dir+f for f in os.listdir(upload_dir)]
    # user_files = [f for f in os.listdir(upload_dir)]
    # os.chdir(upload_dir)
    user_file_stats = []
    for  file in user_files:
        fstat = os.stat(os.path.abspath(file))
        user_file_stats.append([file, (fstat.st_size)/1000, ctime(fstat.st_ctime)])
    print(user_file_stats)
    return read_html("static/user/{}/files.html".format(user))


def handle_entry(request, response, parsed_request_body):
    # print("signup_validity")
    # parsed_request_body = request["body"]
    post_type = parsed_request_body.get("op", False)
    if post_type and post_type == 'login':
        return handle_login(request, response, parsed_request_body)
    return handle_signup(request, response, parsed_request_body)

def handle_post(request, response):
    header = {"Content-Type": "text/html"}
    response["header"].update(header)
    # server.res_header(response, header)
    # server.res_header(response, header)
    # print("handle_post")
    parsed_request_body = request["body"]
    if not 'op' in parsed_request_body:
    # if 'test_upload' in post_from:
        return save_uploads(request, response, parsed_request_body)
    return handle_entry(request, response, parsed_request_body)


def main():
    # Popen(["redis-server"], stdout=PIPE, stderr=PIPE,)
    server.add_route("POST", handle_post)

    server.execute_server()

if __name__ == '__main__':
    os.system("clear||cls")
    main()
