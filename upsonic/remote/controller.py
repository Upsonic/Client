#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import ast



class Upsonic_Remote:
    def _log(self, message):
        self.console.log(message)

    def __enter__(self):
        return self  # pragma: no cover

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # pragma: no cover

    def __init__(self, database_name, api_url, password=None, enable_hashing:bool=False, verify=True):
        import requests
        from requests.auth import HTTPBasicAuth
        from upsonic import console, Upsonic, Upsonic_Serial


        self.force_compress = False
        self.force_encrypt = False
        self.enable_hashing = enable_hashing

        self.verify = verify


        self.console = console
        self.Upsonic = Upsonic
        self.Upsonic_Serial = Upsonic_Serial

        self.requests = requests
        self.HTTPBasicAuth = HTTPBasicAuth


        self.database_name = database_name
        self._log(
            f"[{self.database_name[:5]}*] [bold white]Upsonic Cloud[bold white] initializing...",
        )




        self.api_url = api_url
        self.password = password

        try:
            self.informations = self._informations()
        except TypeError:
            self.informations = None

        self._log(
            f"[{self.database_name[:5]}*] [bold green]Upsonic Cloud[bold green] active",
        )

    def _informations(self):
        return self._send_request("GET", "/informations", make_json=True)

    def debug(self, message):
        data = {"message": message}
        return self._send_request("POST", "/controller/debug", data)

    def info(self, message):
        data = {"message": message}
        return self._send_request("POST", "/controller/info", data)

    def warning(self, message):
        data = {"message": message}
        return self._send_request("POST", "/controller/warning", data)

    def error(self, message):
        data = {"message": message}
        return self._send_request("POST", "/controller/error", data)

    def exception(self, message):
        data = {"message": message}
        return self._send_request("POST", "/controller/exception", data)

    def _send_request(self, method, endpoint, data=None, make_json=False):
        try:
            response = self.requests.request(
                method,
                self.api_url + endpoint,
                data=data,
                auth=self.HTTPBasicAuth("", self.password),
                verify=self.verify
            )
            try:
                response.raise_for_status()
                return response.text if not make_json else json.loads(response.text)
            except self.requests.exceptions.RequestException as e:  # pragma: no cover
                print(f"Error on '{self.api_url + endpoint}': ", response.text)
                return None  # pragma: no cover
        except self.requests.exceptions.ConnectionError:
            print("Error: Remote is down")
            return None

    def set(self, key, value, encryption_key="a", compress=None, cache_policy=0):
        compress = True if self.force_compress else compress
        encryption_key = (
            self.force_encrypt if self.force_encrypt != False else encryption_key
        )

        if encryption_key is not None:
            db = self.Upsonic_Serial(self.database_name, log=False, enable_hashing=self.enable_hashing)
            db.set(key, value, encryption_key=encryption_key)
            value = db.get(key)
            db.delete(key)

        data = {
            "database_name": self.database_name,
            "key": key,
            "value": value,
            "compress": compress,
            "cache_policy": cache_policy,
        }
        return self._send_request("POST", "/controller/set", data)

    def get(self, key, encryption_key="a"):
        encryption_key = (
            self.force_encrypt if self.force_encrypt != False else encryption_key
        )

        data = {"database_name": self.database_name, "key": key}
        response = self._send_request("POST", "/controller/get", data)

        if response is not None:
            if not response == "null\n":
                # Decrypt the received value
                if encryption_key is not None:
                    db = self.Upsonic_Serial(self.database_name, log=False, enable_hashing=self.enable_hashing)
                    db.set(key, response)
                    response = db.get(key, encryption_key=encryption_key)
                    db.delete(key)

                return response
            else:
                return None

    def active(self, value=None, encryption_key="a", compress=None):
        def decorate(value):
            key = value.__name__
            self.set(key, value, encryption_key=encryption_key, compress=compress)

        if value == None:
            return decorate
        else:
            decorate(value)
            return value

    def get_all(self, encryption_key="a"):
        encryption_key = (
            self.force_encrypt if self.force_encrypt != False else encryption_key
        )

        data = {"database_name": self.database_name}
        datas = self._send_request("POST", "/controller/get_all", data)

        datas = json.loads(datas)
        db = self.Upsonic_Serial(self.database_name, log=False, enable_hashing=self.enable_hashing)
        for each in datas:
            db.set(each, datas[each])
            datas[each] = db.get(each, encryption_key=encryption_key)
            db.delete(each)
        return datas

    def delete(self, key):
        data = {"database_name": self.database_name, "key": key}
        return self._send_request("POST", "/controller/delete", data)

    def database_list(self):
        return ast.literal_eval(self._send_request("GET", "/database/list"))


    def database_rename(self, database_name, new_database_name):
        data = {"database_name": database_name, "new_database_name": new_database_name}
        return self._send_request("POST", "/database/rename", data)


    def database_pop(self, database_name):
        data = {"database_name": database_name}
        return self._send_request("POST", "/database/pop", data)

    def database_pop_all(self):
        return self._send_request("GET", "/database/pop_all")

    def database_delete(self, database_name):
        data = {"database_name": database_name}
        return self._send_request("POST", "/database/delete", data)

    def database_delete_all(self):
        return self._send_request("GET", "/database/delete_all")
