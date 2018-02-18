import json
from pprint import pprint
from urllib.parse import urljoin
import requests
from flask.json import jsonify
from requests import request

class CCCli:
    
    with open('megasecretkeyfile.txt', 'r') as r:
        validation_key = r.read()
    
    #server_url = "https://jeshj.pythonanywhere.com"
    server_url = "http://localhost:5000/"

    res = request("GET", server_url)
    print(res.text)
    res.raise_for_status()


    def __init__(self):
        self.get_users()

        while True:
            print("1: Get Users\t2:Set role")
            inp = input("")
            if inp == "1":
                self.get_users()
            if inp == "2":
                self.set_admin()

    def set_admin(self):
        usernumber = input("User number")
        print(self.userlist[usernumber])
        uuid = self.userlist[usernumber]["uuid"]
        print(uuid)
        role = input("1:BASIC\t2:GLOBALADMIN")
        if role == "1":
            rolen = "BASIC"
        elif role == "2":
            rolen = "GLOBALADMIN"
        else:
            return

        d = {"uuid": uuid,
                'role': rolen,
                'validation_key': 123}

        print(d)


        res = requests.post(url=urljoin(self.server_url, "/set_role"), json=d)
        res.raise_for_status()

    def get_users(self):
        res = request('GET', urljoin(self.server_url, "/get_users"))
        res = json.loads(res.text)
        pprint(res)
        self.userlist = res



c = CCCli()
