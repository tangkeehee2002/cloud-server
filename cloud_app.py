#!/usr/bin/env python3
'''handles server side database'''

from os import (mkdir, listdir, stat, system)
from os.path import (abspath, exists)
# from subprocess import (Popen, PIPE)
from crypt import crypt
from hmac import compare_digest as compare_hash
from shutil import copytree
from time import ctime
from jinja2 import Template
import redis
import server


# REDIS_OBJ = redis.StrictRedis("", port=6379)
REDIS_OBJ = redis.StrictRedis()


def handle_login(request, response, login_details):
    # print("handle_login")
    username, passwd = login_details["user"], login_details["password"]
    hashed_passwd = REDIS_OBJ.get(username)
    if hashed_passwd:
        hashed_passwd = hashed_passwd.decode()
        if compare_hash(hashed_passwd, crypt(passwd, hashed_passwd)):
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
    signup_details["password"] = crypt(password)
    # detail_names = [fname, lname, email, username, hashed_passwd]
    user_id = REDIS_OBJ.incr("users")
    REDIS_OBJ.hmset(name="user:{}".format(user_id), mapping=signup_details)
    REDIS_OBJ.hmset(name=username, mapping=signup_details)
    # REDIS_OBJ.hmset(name="user:{}".format(user_id), dict(zip(detail_names, signup_details)))
    # REDIS_OBJ.hmset(name=username, mapping=dict(zip(detail_names, signup_details)))
    REDIS_OBJ.set(username, signup_details["password"])
    REDIS_OBJ.save()
    # REDIS_OBJ.set(username, userid)
    src = abspath("static/login")
    dst = abspath("static/user/{}".format(username))
    if not exists(dst):
        copytree(src, dst)
    mkdir("{}/uploads".format(dst))
    # redirected_path = "user/{}/home.html".format(username)
    # server.redirect(request, response, redirected_path, 307)
    return read_html("static/user/{}/index.html".format(username))# return login page again
#

def read_html(html):
    # print("read_html")
    html_abspath = abspath(html)
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
    upload_dir = "static/user/{}/uploads/".format(user)
    for file, body in parsed_request_body.items():
        filename = abspath(upload_dir + file)
        with open(filename, "wb") as fname:
            fname.write(body["body"])

    # server.redirect(request, response, redirected_path, 307)
    file_page = "static/user/{}/files.html".format(user)
    update_filepage(upload_dir, file_page)
    return read_html("static/user/{}/files.html".format(user))

def update_filepage(upload_dir, file_page):
    file_list = listdir(upload_dir)
    fstat_list = []
    for  num, fname in enumerate(file_list):
        fstat = stat(abspath(upload_dir +"/"+ fname))
        fstat_list.append([num+1, fname, fstat.st_size/1000, ctime(fstat.st_ctime)])
    print(fstat_list)
    template = Template(read_html("static/files_template.html").decode())
    rendered_fpage = template.render(flist_template=fstat_list).encode()
    with open(file_page, "wb+") as fpage:
        fpage.write(rendered_fpage)


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
    system("clear||cls")
    main()
