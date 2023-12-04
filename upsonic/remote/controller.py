#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import ast

from hashlib import sha256

import time

import pickle
import os

import copy

class Upsonic_Remote:
    def _log(self, message):
        self.console.log(message)

    def __enter__(self):
        return self  # pragma: no cover

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # pragma: no cover

    def __init__(self, database_name, api_url, password=None, enable_hashing:bool=False, verify=True, locking=False, client_id=None, cache=False, cache_counter=None, version=False, client_version=False):
        import requests
        from requests.auth import HTTPBasicAuth


        self.force_compress = False
        self.force_encrypt = False
        self.locking = locking
        self.enable_hashing = enable_hashing
        self.cache = cache
        self.cache_counter = cache_counter
        self._cache_counter = {}

        self.local_cache = {}
        
        if self.cache:
           
            self.cache_dir = os.path.join(os.getcwd(), "upsonic_cache")
            if not os.path.exists(self.cache_dir):
                os.mkdir(self.cache_dir)


        self.client_id = client_id

        self.verify = verify

        from upsonic import console

        self.console = console


        self.requests = requests
        self.HTTPBasicAuth = HTTPBasicAuth


        self.database_name = database_name
        self._log(
            f"[{self.database_name[:5]}*] [bold white]Upsonic Cloud[bold white] initializing...",
        )
        
        if self.client_id is not None:
            self._log(f"[{self.database_name[:5]}*] [bold white]Client ID[bold white]: {self.client_id}")
        from upsonic import encrypt, decrypt
        self.encrypt = encrypt
        self.decrypt = decrypt


        self.api_url = api_url
        self.password = password

        try:
            self.informations = self._informations()
        except TypeError:
            self.informations = None

        self._log(
            f"[{self.database_name[:5]}*] [bold green]Upsonic Cloud[bold green] active",
        )
        self._log("---------------------------------------------")

        if self.cache:
            self.cache_hash_load()
            if self._cache_hash is None:
                self._cache_hash = {}
                self.cache_hash_save()



        self.version = version
        self.client_version = client_version
    
    
    def get_set_version_tag(self, client_id=None):
        the_key = "set_version_number"


        
        if client_id is not None:
            the_key = the_key + f"_{client_id}"

        else:
            if self.client_version:
                the_key = the_key + f"_{self.client_id}"            

        the_version = self.get(the_key, no_version=True)
        if the_version is None:
            return None
        if the_version == "latest":
            return None
        return the_version



    def get_get_version_tag(self, client_id=None):
        
        the_key = "get_version_number"


        
        if client_id is not None:
            the_key = the_key + f"_{client_id}"

        else:
            if self.client_version:
                the_key = the_key + f"_{self.client_id}"    


        the_version = self.get(the_key, no_version=True)
        if the_version is None:
            return None
        if the_version == "latest":
            return None
        return the_version


    def set_set_version(self, version_tag, client_id=None):
        the_key = "set_version_number"

        
        if client_id is not None:
            the_key = the_key + f"_{client_id}"

        else:
            if self.client_version:
                the_key = the_key + f"_{self.client_id}"    


        return self.set(the_key, version_tag, no_version=True)

    def set_get_version(self, version_tag, client_id=None):
        the_key = "get_version_number"

        
        if client_id is not None:
            the_key = the_key + f"_{client_id}"

        else:
            if self.client_version:
                the_key = the_key + f"_{self.client_id}"    


        return self.set(the_key, version_tag, no_version=True)


    def cache_hash_save(self):
        
        # Save the cache_hash to workdir/upsonic_cache_hash
        with open(os.path.join(self.cache_dir, "upsonic_cache_hash"), "wb") as f:
            pickle.dump(self._cache_hash, f)
    def cache_hash_load(self):
        # Load the cache_hash from workdir/upsonic_cache_hash
        try:
            with open(os.path.join(self.cache_dir, "upsonic_cache_hash"), "rb") as f:
                self._cache_hash = pickle.load(f)
        except FileNotFoundError:
            self._cache_hash = None
        

    def cache_set(self, key, value):
        self.local_cache[key] = value
        with open(f"{self.cache_dir}/{sha256(key.encode()).hexdigest()}", "wb") as f:
            pickle.dump(value, f)
    def cache_get(self, key):
        if key in self.local_cache:
            return self.local_cache[key]
        with open(f"{self.cache_dir}/{sha256(key.encode()).hexdigest()}", "rb") as f:
            return pickle.load(f)
    def cache_pop(self, key):
        os.remove(f"{self.cache_dir}/{sha256(key.encode()).hexdigest()}")


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


    def _lock_control(self, key, locking_operation=False):
        result = self.get(key+"_lock")
        if result is not None:
            if result == self.client_id and not locking_operation:
                return False
            return True
        return False
  

    def lock_control(self, key):
        if self.locking:
            return self._lock_control(key)
        else:
            return False

    def lock_key(self, key):
        if self._lock_control(key, locking_operation=True):
            self.console.log(f"[bold red] '{key}' is already locked")
            return False

        if self.set(key+"_lock", self.client_id, locking_operation=True) == "Data set successfully":
            self.console.log(f"[bold green] '{key}' is locked")
            return True
        else:
            return False

    def unlock_key(self, key):
        result = self._lock_control(key, locking_operation=True)
        if not result:
            self.console.log(f"[bold red] '{key}' is already unlocked")
            return False
        
        if self._lock_control(key):
            self.console.log(f"[bold red] '{key}' is locked by another client")
            return False

    

        if self.delete(key+"_lock") == "Data deleted successfully":
            self.console.log(f"[bold green] '{key}' is unlocked")
            return True
        else:         
            return False


    def _update_set(self, key):
        self.set(key+"upsonic_updated", sha256(str(time.time()).encode()).hexdigest(), update_operation=True)

    def set(self, key, value, encryption_key="a", compress=None, cache_policy=0, locking_operation=False, update_operation=False, version_tag=None, no_version=False):
        if not locking_operation:
            if self.lock_control(key):
                self.console.log(f"[bold red] '{key}' is locked")
                return None
            
        if not update_operation:
            self._update_set(key)


        compress = True if self.force_compress else compress
        encryption_key = (
            self.force_encrypt if self.force_encrypt != False else encryption_key
        )

        if encryption_key is not None:

            value = self.encrypt(encryption_key, value)


        data = {
            "database_name": self.database_name,
            "key": key,
            "value": value,
            "compress": compress,
            "cache_policy": cache_policy,
        }

        if version_tag is not None:
            copy_data = copy.copy(data)
            copy_data["key"] = copy_data["key"] + f"_upsonic_version_{version_tag}"
            self._send_request("POST", "/controller/set", copy_data)
            if not update_operation:
                self._update_set(copy_data["key"])                     
        elif self.version and not no_version:
            the_version_ = self.get_set_version_tag()

            if the_version_ is not None:
                copy_data = copy.copy(data)
                copy_data["key"] = copy_data["key"] + f"_upsonic_version_{the_version_}"
 
                self._send_request("POST", "/controller/set", copy_data)   
                if not update_operation:
                    self._update_set(copy_data["key"])                             

       

        return self._send_request("POST", "/controller/set", data)

    def get(self, key, encryption_key="a", no_cache=False, version_tag=None, no_version=False):
    

        if version_tag is not None:
            key = key + f"_upsonic_version_{version_tag}"
        elif self.version and not no_version:
            the_version_ = self.get_get_version_tag()
            if the_version_ is not None:
                key = key + f"_upsonic_version_{the_version_}"

        response = None
        if self.cache and not no_cache:
              
                if key not in self._cache_counter:
            
                    self._cache_counter[key] = 0
                self._cache_counter[key] = self._cache_counter[key] + 1
   
                if self._cache_counter[key] < self.cache_counter and self._cache_counter[key] != 1:
                    try:
          
                        response = self.cache_get(key)
          
                    except FileNotFoundError:
  
                        pass
                else:
                    if self._cache_counter[key] >= self.cache_counter:
                        self._cache_counter[key] = 1
                    the_hash = self.get(key+"upsonic_updated", no_cache=True, no_version=True)
                    if key not in self._cache_hash:
                        self._cache_hash[key] = None
                    if the_hash != self._cache_hash[key] and the_hash is not None:
                        self._cache_hash[key] = the_hash
                        self.cache_hash_save()
                        self.console.log("Cache is updated")
                        try:
                            self.cache_pop(key)
                        except FileNotFoundError:
                            pass
                    else:
                        try:
                 
                            response = self.cache_get(key)
                 
                        except FileNotFoundError:
            
                            pass
                   

        encryption_key = (
            self.force_encrypt if self.force_encrypt != False else encryption_key
        )

        data = {"database_name": self.database_name, "key": key}

        if response is None:
    
            response = self._send_request("POST", "/controller/get", data)


        if self.cache:
            self.cache_set(key, response)

        if response is not None:
            if not response == "null\n":
                # Decrypt the received value
                if encryption_key is not None:
                    try:
                        response = self.decrypt(encryption_key, response)
                    except:
                        pass                    
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

        for each in datas:
            if encryption_key is not None:
                try:
                    datas[each] = self.decrypt(encryption_key, datas[each])
                except:
                    pass


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
