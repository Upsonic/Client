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
import textwrap

import cloudpickle

from contextlib import contextmanager

import sys

from rich.progress import Progress

import textwrap
import dill


class Upsonic_On_Prem:
    prevent_enable = False
    quiet_startup = False

    def _log(self, message):
        self.console.log(message)

    def __enter__(self):
        return self  # pragma: no cover

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # pragma: no cover

    def __init__(self, api_url, access_key):
        import requests
        from requests.auth import HTTPBasicAuth

        from upsonic import console

        self.console = console

        self.requests = requests
        self.HTTPBasicAuth = HTTPBasicAuth

        self.api_url = api_url
        self.password = access_key

        self.enable_active = False

        if self.status == True:
            self._log(
                f"[bold green]Upsonic[bold green] active",
            )
        else:
            self._log(
                f"[bold red]Upsonic[bold red] is down",
            )

        from upsonic import encrypt, decrypt

        self.encrypt = encrypt
        self.decrypt = decrypt

        self.thread_number = 5

    def _send_request(self, method, endpoint, data=None, make_json=True):
        try:
            response = self.requests.request(
                method,
                self.api_url + endpoint,
                data=data,
                auth=self.HTTPBasicAuth("", self.password),
                verify=False,
            )
            try:
                result = None
                if not make_json:
                    result = response.text
                else:
                    result = json.loads(response.text)
                    if result["status"] == False:
                        self._log(
                            f"[bold red]Error: {endpoint}",
                        )
                    else:
                        result = result["result"]

                return result
            except:  # pragma: no cover
                print(f"Error on '{self.api_url + endpoint}': ", response.text)
                return [None]  # pragma: no cover
        except:
            print("Error: Remote is down")
            return [None]

    @property
    def status(self):
        return self._send_request("GET", "/status")

    def install_package(self, package):
        from pip._internal import main as pip

        package_name = package.split("==")[0]
        package_version = (
            package.split("==")[1]
            if len(package.split("==")) > 1
            else "Latest"
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
            package.split("==")[1]
            if len(package.split("==")) > 1
            else "Latest"
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

    def load_module(self, module_name, ):
        encryption_key = "u"
        the_all = self.get_all()

        the_all_imports = {}
        for i in the_all:
            if "_upsonic_" in i:
                continue
            name = i.split(".")
            if module_name == name[0]:
                the_all_imports[i] = self.get(i)
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

    def dump_module(
            self,
            module_name,
            module,

    ):
        encryption_key = "u"
        top_module = module

        cloudpickle.register_pickle_by_value(top_module)

        sub_modules = []
        if hasattr(top_module, "__path__"):

            for importer, modname, ispkg in pkgutil.walk_packages(
                    path=top_module.__path__,
                    prefix=top_module.__name__ + ".",
                    onerror=lambda x: None,
            ):
                sub_modules.append(
                    importer.find_module(modname).load_module(modname)
                )
        else:
            sub_modules.append(top_module)

        threads = []

        the_list = []

        for sub_module in sub_modules:
            [
                the_list.append(obj)
                for name, obj in inspect.getmembers(sub_module)
            ]

        # Extract just functions and classes
        the_list = [
            i for i in the_list if inspect.isfunction(i) or inspect.isclass(i)
        ]
        # If the __module__ is not equal to module_name, remove it from the list

        the_list = [
            i for i in the_list if i.__module__.split(".")[0] == module_name
        ]

        my_list = []
        for element in copy.copy(the_list):
            if inspect.isfunction(element):
                name = element.__module__ + "." + element.__name__

            elif inspect.isclass(element):
                name = element.__module__ + "." + element.__name__
            if (
                    not "upsonic.remote" in name
                    and not "upsonic_updater" in name
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

    def dump(
            self,
            key,
            value,

    ):

        return self.set(
            key,
            value,
        )

    def load(
            self,
            key,
    ):
        return self.get(
            key,
        )

    def set(
            self,
            key,
            value,
    ):

        the_type = type(value).__name__
        if the_type == "type":
            the_type = "class"

        encryption_key = "u"
        liberty = True

        data = {
            "scope": key,
            "data": self.encrypt(encryption_key, value, liberty=liberty),
        }

        self._send_request("POST", "/dump", data)

        data = {"scope": key, "type": the_type}

        self._send_request("POST", "/dump_type", data)

        data = {
            "scope": key,
            "code": textwrap.dedent(dill.source.getsource(value)),
        }

        self._send_request("POST", "/dump_code", data)

        return True

    def get(
            self,
            key,

    ):
        response = None

        encryption_key = "u"

        data = {"scope": key}

        if response is None:
            response = self._send_request("POST", "/load", data)

        response = self.decrypt(encryption_key, response)
        return response

    def active(
            self,
            value=None,

    ):
        encryption_key = "u"

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
            )

        if value == None:
            return decorate
        else:
            decorate(value)
            return value

    def get_all(self, ):
        encryption_key = "u"

        datas = self._send_request("GET", "/get_all_scopes_user")
        return datas

    def delete(self, key):
        data = {"database_name": self.database_name, "key": key}
        self.cache_pop(key)
        return self._send_request("POST", "/controller/delete", data)

    def database_list(self):
        return ast.literal_eval(self._send_request("GET", "/database/list"))

    def database_rename(self, database_name, new_database_name):
        data = {
            "database_name": database_name,
            "new_database_name": new_database_name,
        }
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