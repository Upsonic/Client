#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import ast

from hashlib import sha256


import pickle
import os

import copy

import inspect
import pkgutil
import threading
import time

import cloudpickle


from contextlib import contextmanager

import sys

from rich.progress import Progress


class Upsonic_Remote:
    prevent_enable = False
    quiet_startup = False

    def _log(self, message):
        if not self.quiet:
            self.console.log(message)

    def __enter__(self):
        return self  # pragma: no cover

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # pragma: no cover

    def __init__(
        self,
        database_name,
        api_url,
        password=None,
        enable_hashing: bool = False,
        verify=True,
        locking=False,
        client_id=None,
        cache=False,
        cache_counter=None,
        version=False,
        client_version=False,
        key_encyption=False,
        meta_datas=True,
        quiet=False,
        thread_number=1,
    ):
        import requests
        from requests.auth import HTTPBasicAuth

        self.thread_number = thread_number

        self.quiet = quiet

        self.meta_datas = meta_datas

        self.force_compress = False
        self.force_encrypt = False
        self.key_encyption = key_encyption
        self.locking = locking
        self.enable_hashing = enable_hashing
        self.cache = cache
        self.cache_counter = cache_counter
        self._cache_counter = {}

        self.local_cache = {}

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
        if not Upsonic_Remote.quiet_startup:
            self._log(
                f"[{self.database_name[:5]}*] [bold white]Upsonic Cloud[bold white] initializing...",
            )

        if self.client_id is not None:
            if not Upsonic_Remote.quiet_startup:
                self._log(
                    f"[{self.database_name[:5]}*] [bold white]Client ID[bold white]: {self.client_id}"
                )
        from upsonic import encrypt, decrypt

        self.encrypt = encrypt
        self.decrypt = decrypt

        self.api_url = api_url
        self.password = password

        try:
            self.informations = self._informations()
        except TypeError:
            self.informations = None
        if self.informations is not None:
            rate_limits = self.informations["rate_limit"][1]
            rate_limits = rate_limits.split(" ")
            self.rate_limit = int(rate_limits[1])
            self.thread_number = 10

        if not Upsonic_Remote.quiet_startup:
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

        self.enable_active = False

    def install_package(self, package):
        from pip._internal import main as pip

        package_name = package.split("==")[0]
        package_version = (
            package.split("==")[1] if len(package.split("==")) > 1 else "Latest"
        )

        the_dir = os.path.abspath(
            os.path.join(self.cache_dir, package_name, package_version)
        )
        if not os.path.exists(the_dir):
            os.makedirs(the_dir)

        pip(["install", package, "--target", the_dir])

    @contextmanager
    def import_package(self, package):
        """
        import sys
        for a in list(sys.modules):
            if a.startswith("numpy"):
                del sys.modules[a]
        """

        package_name = package.split("==")[0]
        package_version = (
            package.split("==")[1] if len(package.split("==")) > 1 else "Latest"
        )

        the_dir = os.path.abspath(
            os.path.join(self.cache_dir, package_name, package_version)
        )

        if not os.path.exists(the_dir):
            self.install_package(package)

        sys_path_backup = sys.path.copy()

        sys.path.insert(0, the_dir)

        try:
            yield
        finally:
            sys.path = sys_path_backup

    def extend_global(self, name, value):
        globals()[name] = value

    def load_module(self, module_name, encryption_key="a"):
        the_all = self.get_all(encryption_key=encryption_key)
        the_all_imports = {}
        for i, value in the_all.items():
            if "_upsonic_" in i:
                continue
            name = i.split(".")
            if module_name == name[0]:
                the_all_imports[i] = value
        import types

        def create_module_obj(dictionary):
            result = {}
            for key, value in dictionary.items():
                modules = key.split(".")
                current_dict = result
                for module in modules[:-1]:
                    if module not in current_dict:
                        current_dict[module] = types.ModuleType(module)
                    current_dict = vars(current_dict[module])
                current_dict[modules[-1]] = value

            return result

        generated_library = create_module_obj(the_all_imports)[module_name]

        return generated_library

    def enable(self, encryption_key="a", the_globals={}):
        the_keys = {}
        if Upsonic_Remote.prevent_enable:
            return the_keys.items()

        from upsonic import interface

        for key, value in the_globals.items():
            setattr(interface, key, value)
            globals()[key] = value

        self._log("[bold white]Syncing with Upsonic Cloud...")
        self.enable_active = True

        the_all_imports = {}

        the_us = self
        # Register the_us to globals
        globals()["the_us"] = the_us

        the_all = self.get_all(encryption_key=encryption_key)

        for key, value in the_all.items():
            if "_upsonic_" not in key:
                try:
                    original_key = key
                    original_key_without_dow = key.replace(".", "_")

                    key = key.split(".")
                    message = value

                    from upsonic import interface

                    setattr(interface, key[-1], copy.copy(message))
                    the_keys[key[-1]] = copy.copy(message)

                except:
                    import traceback

                    traceback.print_exc()
                    self._log(f"[bold white]Error on patching '{key}'")

        return the_keys.items()

    def dump_module(
        self, module_name, module, encryption_key="a", compress=None, liberty=True
    ):
        top_module = module

        cloudpickle.register_pickle_by_value(top_module)

        sub_modules = []
        if hasattr(top_module, "__path__"):
            for importer, modname, ispkg in pkgutil.walk_packages(
                path=top_module.__path__,
                prefix=top_module.__name__ + ".",
                onerror=lambda x: None,
            ):
                sub_modules.append(importer.find_module(modname).load_module(modname))
        else:
            sub_modules.append(top_module)

        threads = []

        the_list = []

        for sub_module in sub_modules:
            [the_list.append(obj) for name, obj in inspect.getmembers(sub_module)]

        # Extract just functions and classes
        the_list = [i for i in the_list if inspect.isfunction(i) or inspect.isclass(i)]
        # If the __module__ is not equal to module_name, remove it from the list

        the_list = [i for i in the_list if i.__module__.split(".")[0] == module_name]

        my_list = []
        for element in copy.copy(the_list):
            if inspect.isfunction(element):
                name = element.__module__ + "." + element.__name__

            elif inspect.isclass(element):
                name = element.__module__ + "." + element.__name__
            if (
                "upsonic.remote" not in name
                and "upsonic_updater" not in name
                and name != f"{module.__name__}.threading.Thread"
            ):
                my_list.append(element)

        the_list = my_list

        with Progress() as progress:
            task1 = progress.add_task(
                "           [red]Job Started...", total=len(the_list)
            )
            task2 = progress.add_task(
                "           [green]Job Complated...", total=len(the_list)
            )

            for element in the_list:
                time.sleep(0.1)
                if inspect.isfunction(element):
                    name = element.__module__ + "." + element.__name__

                elif inspect.isclass(element):
                    name = element.__module__ + "." + element.__name__
                else:
                    continue

                first_element = name.split(".")[0]

                if first_element != module_name:
                    continue

                try:
                    while len(threads) >= self.thread_number:
                        for each in threads:
                            if not each.is_alive():
                                threads.remove(each)
                        time.sleep(0.1)

                    the_thread = threading.Thread(
                        target=self.set,
                        args=(name, element),
                        kwargs={
                            "encryption_key": encryption_key,
                            "compress": compress,
                            "liberty": liberty,
                        },
                    )
                    the_thread.start()

                    thread = the_thread
                    threads.append(thread)
                    progress.update(task1, advance=1)

                except:
                    import traceback

                    traceback.print_exc()
                    self._log(f"[bold red]Error on '{name}'")
                    self.delete(name)

            for each in threads:
                progress.update(task2, advance=1)
                each.join()

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
        if key in self.local_cache:
            self.local_cache.pop(key)
        try:
            os.remove(f"{self.cache_dir}/{sha256(key.encode()).hexdigest()}")
        except:
            pass

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
                verify=self.verify,
            )

            try:
                response.raise_for_status()
                return response.text if not make_json else json.loads(response.text)
            except self.requests.exceptions.RequestException:  # pragma: no cover
                print(f"Error on '{self.api_url + endpoint}': ", response.text)
                return None  # pragma: no cover
        except self.requests.exceptions.ConnectionError:
            print("Error: Remote is down")
            return None

    def _lock_control(self, key, locking_operation=False):
        the_client_id = self.client_id
        if the_client_id is None:
            the_client_id = "Unknown"

        result = self.get(key + "_upsonic_lock", encryption_key=None, no_cache=True)
        if result is not None:
            result = result[1:]
            result = result[:-2]
            if result == the_client_id and not locking_operation:
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
            self._log(f"[bold red] '{key}' is already locked")
            return False

        the_client_id = self.client_id
        if the_client_id is None:
            the_client_id = "Unknown"

        if (
            self.set(
                key + "_upsonic_lock",
                the_client_id,
                locking_operation=True,
                encryption_key=None,
                no_cache=True,
            )
            == "Data set successfully"
        ):
            self._log(f"[bold green] '{key}' is locked")
            return True
        else:
            return False

    def unlock_key(self, key):
        result = self._lock_control(key, locking_operation=True)
        if not result:
            self._log(f"[bold red] '{key}' is already unlocked")
            return False

        if self._lock_control(key):
            self._log(f"[bold red] '{key}' is locked by another client")
            return False

        if self.delete(key + "_upsonic_lock") == "Data deleted successfully":
            self._log(f"[bold green] '{key}' is unlocked")
            return True
        else:
            return False

    def _update_set(self, key, meta):
        if self.meta_datas:
            return self.set(
                key + "_upsonic_meta", meta, update_operation=True, encryption_key=None
            )

    def _liberty_set(self, key, liberty_class):
        if liberty_class:
            self.set(
                key + "_upsonic_liberty_class",
                True,
                update_operation=True,
                encryption_key=None,
            )
        else:
            self.delete(key + "_upsonic_liberty_class")
        return self.set(
            key + "_upsonic_liberty", True, update_operation=True, encryption_key=None
        )

    def _liberty_unset(self, key, liberty_class):
        if liberty_class:
            self.delete(key + "_upsonic_liberty_class")
        self.delete(key + "_upsonic_liberty")

    def dump(
        self,
        key,
        value,
        encryption_key="a",
        compress=None,
        cache_policy=0,
        locking_operation=False,
        update_operation=False,
        version_tag=None,
        no_version=False,
        liberty=True,
    ):
        return self.set(
            key,
            value,
            encryption_key=encryption_key,
            compress=compress,
            cache_policy=cache_policy,
            locking_operation=locking_operation,
            update_operation=update_operation,
            version_tag=version_tag,
            no_version=no_version,
            liberty=liberty,
        )

    def load(
        self,
        key,
        encryption_key="a",
        no_cache=False,
        version_tag=None,
        no_version=False,
    ):
        return self.get(
            key,
            encryption_key=encryption_key,
            no_cache=no_cache,
            version_tag=version_tag,
            no_version=no_version,
        )

    def set(
        self,
        key,
        value,
        encryption_key="a",
        compress=None,
        cache_policy=0,
        locking_operation=False,
        update_operation=False,
        version_tag=None,
        no_version=False,
        liberty=True,
    ):
        self.cache_pop(key)
        if not locking_operation:
            if self.lock_control(key):
                self._log(f"[bold red] '{key}' is locked")
                return None

        the_type = type(value).__name__
        if the_type == "type":
            the_type = "class"

        meta = {"type_of_value": the_type}
        meta = json.dumps(meta)

        compress = True if self.force_compress else compress
        encryption_key = (
            self.force_encrypt if self.force_encrypt != False else encryption_key
        )

        liberty_class = inspect.isclass(value)
        if encryption_key is not None:
            value = self.encrypt(encryption_key, value, liberty=liberty)

        if "_upsonic_" not in key:
            if liberty:
                self._liberty_set(key, liberty_class)
            else:
                self._liberty_unset(key, liberty_class)

        key = sha256(key.encode()).hexdigest() if self.key_encyption else key

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
                self._update_set(copy_data["key"], meta)
        elif self.version and not no_version:
            the_version_ = self.get_set_version_tag()

            if the_version_ is not None:
                copy_data = copy.copy(data)
                copy_data["key"] = copy_data["key"] + f"_upsonic_version_{the_version_}"

                self._send_request("POST", "/controller/set", copy_data)
                if not update_operation:
                    self._update_set(copy_data["key"], meta)

        if not update_operation:
            self._update_set(key, meta)
        return self._send_request("POST", "/controller/set", data)

    def get(
        self,
        key,
        encryption_key="a",
        no_cache=False,
        version_tag=None,
        no_version=False,
    ):
        key = sha256(key.encode()).hexdigest() if self.key_encyption else key

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

            if (
                self._cache_counter[key] < self.cache_counter
                and self._cache_counter[key] != 1
            ):
                try:
                    response = self.cache_get(key)

                except FileNotFoundError:
                    pass
            else:
                if self._cache_counter[key] >= self.cache_counter:
                    self._cache_counter[key] = 1
                the_hash = self.get(
                    key + "_upsonic_updated", no_cache=True, no_version=True
                )
                if key not in self._cache_hash:
                    self._cache_hash[key] = None
                if the_hash != self._cache_hash[key] and the_hash is not None:
                    self._cache_hash[key] = the_hash
                    self.cache_hash_save()
                    self._log("Cache is updated")
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
                        import traceback

                        traceback.print_exc()
                        pass
                return response
            else:
                return None

    def active(
        self,
        value=None,
        encryption_key="a",
        compress=None,
        just_name=False,
        liberty=True,
    ):
        def decorate(value):
            key = value.__name__
            if (
                value.__module__ != "__main__"
                and value.__module__ != None
                and not just_name
            ):
                key = value.__module__ + "." + key
            self.set(
                key,
                value,
                encryption_key=encryption_key,
                compress=compress,
                liberty=liberty,
            )

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
        self.cache_pop(key)
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
