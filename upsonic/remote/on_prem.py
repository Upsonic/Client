#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import ast
from functools import wraps


import pickle
import os
import re

import copy
from cryptography.fernet import Fernet
import base64
import hashlib
import inspect
import pkgutil
import threading
import time
import textwrap
import importlib.util
import cloudpickle

from contextlib import contextmanager

import sys

from rich.progress import Progress

import dill

from pip._internal.operations import freeze

import traceback
import shutil
from memory_profiler import memory_usage


from rich.console import Console

console = Console()

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from remote.localimport import localimport
from remote.interface import encrypt
from remote.interface import decrypt

import platform


def extract_needed_libraries(func, debug=False):
    result = {}
    the_globals = dill.detect.globalvars(func)
    for each in the_globals:
        name = dill.source.getname(the_globals[each], fqn=True)
        result[each] = name.split(".")[0]
    print("result", result) if debug else None
    return result





def extract_source(obj, key=None, debug=False):
    result = None
    try:
        result = inspect.getsource(obj)
    except:
        try:
            result = dill.source.getsource(obj)
        except:
            pass
    
    if result == None:
        try:
            value = None
            if isinstance(obj, str):
                value = '"'+str(obj)+'"'
            else:
                value = str(obj)
            result = key.split(".")[-1] + "=" + value
        except:
            traceback.print_exc()


    if result == None:
       my_source = "Error on extracting source"
    else:
        my_source = result
    return my_source


def extract_local_files(obj, debug=False, local_directory=None):
    if local_directory == None:
        local_directory = os.getcwd()
    print(local_directory) if debug else None

    the_elements = dill.detect.globalvars(obj)
    print(the_elements) if debug else None
    the_local_elements = {}
    for element, value in the_elements.items():
        element_file = dill.source.getfile(value)
        print(element_file) if debug else None
        if element_file.startswith(local_directory):
            print("Inside") if debug else None
            with open(element_file, "r") as f:
                element_content = f.read()
            print("element_content", element_content) if debug else None
            the_local_elements[os.path.basename(element_file)] = element_content

    print("Complated") if debug else None
    return the_local_elements


def dump_local_files(extract, debug=False, local_directory=None):
    if local_directory == None:
        local_directory = os.getcwd()
    print(local_directory) if debug else None

    for element, value in extract.items():
        # Create a directory named as upsonic if not exists
        if not os.path.exists(os.path.join(local_directory, "upsonic")):
            os.makedirs(os.path.join(local_directory, "upsonic"))

        file_location = os.path.join(local_directory, "upsonic", element)
        print(file_location) if debug else None
        print(value) if debug else None
        with open(file_location, "w") as f:
            f.write(value)

        sys.path.insert(0, os.path.join(local_directory, "upsonic"))


class Upsonic_On_Prem:
    prevent_enable = False
    quiet_startup = False

    @staticmethod
    def export_requirement():
        the_list = list(freeze.freeze())
        the_string = ""
        for item in the_list:
            the_string += item + ", "
        return the_string[:-2]

    def _log(self, message):
        self.console.log(message)

    def __enter__(self):
        return self  # pragma: no cover

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # pragma: no cover

    @property
    def console(self):
        return console

    @property
    def localimport(self):
        return localimport

    @property
    def encrypt(self):
        return encrypt

    @property
    def decrypt(self):
        return decrypt

    def __init__(
        self,
        api_url,
        access_key,
        engine="cloudpickle,dill",
        enable_usage_analyses=True,
        enable_local_files=True,
        enable_auto_requirements=False,
        enable_elastic_dependency=False,
        cache_dir=None,
        pass_python_version_check=False,
        byref=True,
        recurse=True,
        protocol=pickle.DEFAULT_PROTOCOL,
        source=True,
        builtin=True,
        tester=False,
    ):
        import requests
        from requests.auth import HTTPBasicAuth

        from requests.packages.urllib3.exceptions import InsecureRequestWarning

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.requests = requests
        self.HTTPBasicAuth = HTTPBasicAuth

        self.api_url = api_url
        self.password = access_key
        self.engine = engine
        self.byref = byref
        self.recurse = recurse
        self.protocol = protocol
        self.source = source
        self.builtin = builtin
        self.enable_auto_requirements = enable_auto_requirements
        self.enable_elastic_dependency = enable_elastic_dependency
        self.enable_usage_analyses = enable_usage_analyses
        self.enable_local_files = enable_local_files

        self.tester = tester
        self.pass_python_version_check = pass_python_version_check

        self.enable_active = False

        self.cache_dir = (
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "upsonic_cache")
            if cache_dir == None
            else cache_dir
        )
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)

        if self.status == True:
            self._log(
                "[bold green]Upsonic[bold green] active",
            )
        else:
            self._log(
                "[bold red]Upsonic[bold red] is down",
            )

        self.thread_number = 5

    def _send_request(
        self, method, endpoint, data=None, make_json=True, include_status=False
    ):
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
                        result = result["result"] if not include_status else result

                return result
            except:  # pragma: no cover
                print(
                    f"Error on '{self.api_url + endpoint}': ", response.text
                ) if self.tester else None
                return [None]  # pragma: no cover
        except:
            print("Error: Remote is down")
            return [None]

    @property
    def status(self):
        return self._send_request("GET", "/status")

    def get_specific_version(self, package):
        package_name = package.split("==")[0]
        package_version = (
            package.split("==")[1] if len(package.split("==")) > 1 else "Latest"
        )
        backup_sys_path = sys.path
        backup_sys_modules = sys.modules

        the_dir = os.path.abspath(
            os.path.join(self.cache_dir, package_name, package_version)
        )
        with self.localimport(the_dir) as _importer:
            return importlib.import_module(package_name)

    def generate_the_globals(self, needed_libraries, key):
        requirements = self.extract_the_requirements(key)

        total = {}
        for each, value in needed_libraries.items():
            the_needed = None
            for each_r in requirements:
                each_r_ = each_r.split("==")[0]
                if each_r_.split(".")[0].lower() == value.split(".")[0].lower():
                    total[each] = self.get_specific_version(each_r.lower())

        return total

    def generate_the_true_requirements(self, requirements, needed_libraries, key):
        total = {}
        for each, value in needed_libraries.items():
            the_needed = None
            for each_r in requirements:
                each_r_ = each_r.split("==")[0]
                if each_r_.split(".")[0].lower() == value.split(".")[0].lower():
                    total[each] = each_r

        return total

    def install_package(self, package):
        from pip._internal import main as pip

        package_name = package.split("==")[0]
        package_version = (
            package.split("==")[1] if len(package.split("==")) > 1 else "Latest"
        )

        the_dir = os.path.abspath(
            os.path.join(self.cache_dir, package_name, package_version)
        )
        if not os.path.exists(the_dir) or not self.enable_elastic_dependency:
            if self.enable_elastic_dependency:
                os.makedirs(the_dir)
                if self.tester:
                    self._log(f"Installing {package} to {the_dir}")
                pip(["install", package, "--target", the_dir, "--no-dependencies"])
            else:
                if self.tester:
                    self._log(f"Installing {package} to default_dir")
                pip(["install", package])

    def extract_the_requirements(self, key):
        the_requirements = self.get_requirements(key)
        elements = []
        for each in the_requirements.split(","):
            if "==" in each:
                the_requirement = textwrap.dedent(each)
                elements.append(the_requirement)
        return elements

    def install_the_requirements(self, the_requirements):
        installed_requirements = self.export_requirement()
        if self.tester:
            self._log(f"installed_requirements {installed_requirements}")
        try:
            installed_requirements = installed_requirements.lower()
        except:
            pass

        for each in the_requirements:
            try:
                if each not in installed_requirements or self.enable_elastic_dependency:
                    self.install_package(each)
                else:
                    if self.tester:
                        self._log("Already installed in system")
            except:
                if self.tester:
                    self._log(f"Error on {each}")
                    traceback.print_exc()

    def delete_cache(self):
        shutil.rmtree(self.cache_dir)

    def set_the_library_specific_locations(self, the_requirements):
        the_all_dirs = []
        the_all_string = ""

        ordered_list = sorted(the_requirements)
        if self.tester:
            self._log(f"ordered_list {ordered_list}")

        for package in ordered_list:
            package_name = package.split("==")[0]
            package_version = (
                package.split("==")[1] if len(package.split("==")) > 1 else "Latest"
            )
            the_all_string += package

            the_dir = os.path.abspath(
                os.path.join(self.cache_dir, package_name, package_version)
            )

            the_all_dirs.append(the_dir)
        if self.tester:
            self._log(f"the_all_string {the_all_string}")

        # Create folder with sha256 of the_all_string
        sha256_string = hashlib.sha256(the_all_string.encode("utf-8")).hexdigest()
        sha256_dir = os.path.join(self.cache_dir, sha256_string)
        already_exist = os.path.exists(sha256_dir)
        os.makedirs(sha256_dir, exist_ok=True)

        if not already_exist:
            # Copying all contents in the_all_dirs to sha256_dir
            for dir_path in the_all_dirs:
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        # construct full file path
                        full_file_name = os.path.join(root, file)
                        # construct destination path
                        dest_file_name = sha256_dir + full_file_name[len(dir_path) :]
                        # create directories if not present in destination
                        os.makedirs(os.path.dirname(dest_file_name), exist_ok=True)
                        # copy file
                        shutil.copy(full_file_name, dest_file_name)

        if self.tester:
            self._log(f"the sha256 of new directory {already_exist} {sha256_dir}")

        return sha256_dir

    def unset_the_library_specific_locations(self):
        sys.path = self.sys_path_backup

    @contextmanager
    def import_package(self, package):
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

    def load_module(self, module_name, version=None):
        encryption_key = "u"

        version_check_pass = False
        the_all = self.get_all()
        original_name = module_name
        sub_module_name = False
        if "." in module_name:
            sub_module_name = module_name.replace(".", "_")
            module_name = sub_module_name

        the_all_imports = {}
        for i in the_all:
            original_i = i
            if "_upsonic_" in i:
                continue
            if sub_module_name != False:
                i = i.replace(original_name, module_name)
            name = i.split(".")
            if module_name == name[0]:
                try:
                    if not self.pass_python_version_check and not version_check_pass:
                        key_version = self.get_python_version(original_i)
                        currenly_version = self.get_currently_version()
                        if self.tester:
                            self._log(f"key_version {key_version}")
                            self._log(f"currenly_version {currenly_version}")
                        if (
                            key_version[0] == currenly_version[0]
                            and key_version[0] == "3"
                        ):
                            if self.tester:
                                self._log("Versions are same and 3")
                            if key_version[1] != currenly_version[1]:
                                if self.tester:
                                    self._log("Minor versions are different")

                                self._log(
                                    "[bold orange]Warning: The versions are different, are you sure to continue"
                                )
                                the_input = input("Yes or no (y/n)").lower()
                                if the_input == "n":
                                    key_version = f"{key_version[0]}.{key_version[1]}"
                                    currenly_version = (
                                        f"{currenly_version[0]}.{currenly_version[1]}"
                                    )
                                    return (
                                        "Python versions is different (Key == "
                                        + key_version
                                        + " This runtime == "
                                        + currenly_version
                                        + ")"
                                    )
                                if the_input == "y":
                                    version_check_pass = True
                except:
                    if self.tester:
                        traceback.print_exc()

                if version != None:
                    version_list_response = self.get_version_history(original_i)
                    version_list = []
                    for each_v in version_list_response:
                        version_list.append(each_v.replace(original_i + ":", ""))

                    if version in version_list:
                        try:
                            the_all_imports[i] = self.get(
                                original_i, version, pass_python_version_control=True
                            )
                        except:
                            the_all_imports[i] = self.get(
                                original_i, pass_python_version_control=True
                            )
                else:
                    the_all_imports[i] = self.get(
                        original_i, pass_python_version_control=True
                    )

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
        message=None,
    ):
        return self.set(key, value, message=message)

    def load(self, key, version=None):
        return self.get(key, version=version, print_exc=True)

    def get_currently_version(self):
        total = sys.version_info
        the_version = []
        the_version.append(total.major)
        the_version.append(total.minor)
        the_version.append(total.micro)
        return the_version

    def get_python_version(self, key):
        data = {"scope": key}
        total = self._send_request("POST", "/get_python_version_of_scope", data)
        the_version = []
        the_version.append(int(total.split(".")[0]))
        the_version.append(int(total.split(".")[1]))
        the_version.append(int(total.split(".")[2]))
        return the_version

    def get_lock(self, key):
        data = {"scope": key}
        lock = self._send_request("POST", "/get_lock_of_scope", data)
        return lock

    def set(self, key, value, message=None):


        if isinstance(value, str):
            pass
        elif isinstance(value, int):
            pass
        elif isinstance(value, float):
            pass
        elif callable(value):
            pass
        else:
            self._log("Error: Upsonic only supports string, integer, float, and functions.")
            return False







        if key.startswith("."):
            self._log("Error: The key can not start with '.'")
            return False
        if ":" in key:
            self._log("Error: The key can not include ':'")
            return False
        if key.endswith("."):
            self._log("Error: The key can not end with '.'")
            return False
        if "." not in key:
            self._log("Error: You should create a parent with '.' like math.sum")
            return False
        if ".." in key:
            self._log("Error: The key can not include multiple dot one after one'..'")
            return False

        try:
            the_lock = self.get_lock(key)
            if the_lock and the_lock != [None]:
                self._log("This scope is locked now! Someone dumping.")
                return False
        except:
            pass

        the_type = type(value).__name__
        if the_type == "type":
            the_type = "class"

        encryption_key = "u"

        the_code = textwrap.dedent(extract_source(value, key=key))

        the_requirements = Upsonic_On_Prem.export_requirement()
        the_original_requirements = ""
        if self.tester:
            self._log(f"The first original requirements {the_original_requirements}")
        elements = []
        for each in the_requirements.split(","):
            if "==" in each:
                the_requirement = textwrap.dedent(each)
                elements.append(the_requirement)
        the_requirements = elements
        if self.tester:
            self._log(f"the_requirements {the_requirements}")

        extracted_needed_libraries = None
        try:
            extracted_needed_libraries = extract_needed_libraries(value, self.tester)
            try:
                the_original_requirements = self.generate_the_true_requirements(
                    the_requirements, extracted_needed_libraries, key
                )
                if self.tester:
                    self._log(
                        f"the_original_requirements in_generation {the_original_requirements}"
                    )
                the_text = ""
                for each, value_ in the_original_requirements.items():
                    the_text += value_ + ", "
                the_original_requirements = the_text[:-2]

            except:
                if self.tester:
                    self._log(
                        f"Error on generate_the_true_requirements while dumping {key}"
                    )
                    traceback.print_exc()
        except:
            if self.tester:
                self._log(f"Error on extract_needed_libraries while dumping {key}")
                traceback.print_exc()

        if self.tester:
            self._log(f"the_original_requirements {the_original_requirements}")

        the_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        fernet_key = base64.urlsafe_b64encode(
            hashlib.sha256(encryption_key.encode()).digest()
        )
        fernet = Fernet(fernet_key)

        engine_reports_exceptions = []
        the_engine_reports = {}
        for engine in self.engine.split(","):
            try:
                the_engine_reports[engine] = self.encrypt(
                    encryption_key,
                    value,
                    engine,
                    self.byref,
                    self.recurse,
                    self.protocol,
                    self.source,
                    self.builtin,
                )
            except:
                if self.tester:
                    self._log(f"Error on {engine} while dumping {key}")
                    traceback.print_exc()
                else:
                    engine_reports_exceptions.append(traceback.format_exc())

        if len(the_engine_reports) == 0 and not self.tester:
            self._log("[red] Error: No engine is able to dump the object")
            for error in engine_reports_exceptions:
                print(error)

        try:
            the_engine_reports["extracted_local_files"] = fernet.encrypt(
                pickle.dumps(extract_local_files(value, self.tester), protocol=1)
            )
        except:
            if self.tester:
                self._log(f"Error on extracted_local_files while dumping {key}")
                traceback.print_exc()

        try:
            the_engine_reports["extract_source"] = fernet.encrypt(
                pickle.dumps(extract_source(value, debug=self.tester, key=key), protocol=1)
            )
        except:
            if self.tester:
                self._log(f"Error on extract_source while dumping {key}")
                traceback.print_exc()

        if extracted_needed_libraries != None:
            the_engine_reports["extract_needed_libraries"] = fernet.encrypt(
                pickle.dumps(extracted_needed_libraries, protocol=1)
            )

        if self.tester:
            self._log(f"the_engine_reports {the_engine_reports}")
        dumped = pickle.dumps(the_engine_reports, protocol=1)

        data = {
            "scope": key,
            "code": the_code,
            "type": the_type,
            "requirements": the_original_requirements,
            "python_version": the_version,
            "data": fernet.encrypt(dumped),
            "commit_message": message,
        }

        response = self._send_request(
            "POST", "/dump_together", data, include_status=True
        )

        if response != [None]:
            if response["status"] is False:
                return response["result"]

            if response["status"] is True:
                return True
        else:
            return False

    def print_code(self, key, version=None):
        print(self.get(key, version=version, extract_source=True))

    def get(
        self,
        key,
        version=None,
        print_exc=True,
        pass_python_version_control=False,
        pass_usage_analyses=False,
        try_to_extract_importable=False,
        extract_source=False,
    ):
        if self.tester:
            self._log(f"Process started for {key}")
        response = None

        encryption_key = "u"

        data = {"scope": key}

        versions_are_different = False
        if pass_python_version_control:
            versions_are_different = True
        try:
            if not self.pass_python_version_check and not pass_python_version_control:
                key_version = self.get_python_version(key)
                currenly_version = self.get_currently_version()
                if self.tester:
                    self._log(f"key_version {key_version}")
                    self._log(f"currenly_version {currenly_version}")
                if key_version[0] == currenly_version[0] and key_version[0] == 3:
                    if self.tester:
                        self._log("Versions are same and 3")
                    if key_version[1] != currenly_version[1]:
                        if self.tester:
                            self._log("Minor versions are different")
                        if int(currenly_version[1]) >= 11 or int(key_version[1]) >= 11:
                            if (
                                int(currenly_version[1]) < 11
                                or int(key_version[1]) < 11
                            ):
                                versions_are_different = True
                                self._log(
                                    "[bold orange]Warning: The versions are different, are you sure to continue"
                                )
                                the_input = input("Yes or no (y/n)").lower()
                                if the_input == "n":
                                    key_version = f"{key_version[0]}.{key_version[1]}"
                                    currenly_version = (
                                        f"{currenly_version[0]}.{currenly_version[1]}"
                                    )
                                    return (
                                        "Python versions is different (Key == "
                                        + key_version
                                        + " This runtime == "
                                        + currenly_version
                                        + ")"
                                    )
        except:
            if self.tester:
                traceback.print_exc()

        the_requirements_path = None

        if self.enable_auto_requirements:
            try:
                the_requirements = self.extract_the_requirements(key)

                self.install_the_requirements(the_requirements)
                if self.tester:
                    self._log(f"the_requirements {the_requirements}")
                if self.enable_elastic_dependency:
                    the_requirements_path = self.set_the_library_specific_locations(
                        the_requirements
                    )
            except:
                if self.tester:
                    self._log(f"Error on requirements while dumping {key}")
                    traceback.print_exc()

        if response is None:
            if version != None:
                response = self.get_version_data(key, version)
            else:
                response = self._send_request("POST", "/load", data)
        try:
            fernet_key = base64.urlsafe_b64encode(
                hashlib.sha256(encryption_key.encode()).digest()
            )
            fernet = Fernet(fernet_key)
            response = pickle.loads(fernet.decrypt(response))
            if self.tester:
                self._log(f"response {response}")
            if "extracted_local_files" in response:
                try:
                    if self.enable_local_files:
                        dump_local_files(
                            pickle.loads(
                                fernet.decrypt(response["extracted_local_files"])
                            ),
                            self.tester,
                        )
                    else:
                        if self.tester:
                            self._log("Local files are not enabled")
                except:
                    if self.tester:
                        self._log(f"Error on extracted_local_files while loading {key}")
                        traceback.print_exc()
                response.pop("extracted_local_files")
            if extract_source:
                return pickle.loads(fernet.decrypt(response["extract_source"]))
            if "extract_source" in response:
                response.pop("extract_source")
            needed_libraries = None
            if "extract_needed_libraries" in response:
                needed_libraries = pickle.loads(
                    fernet.decrypt(response["extract_needed_libraries"])
                )
                response.pop("extract_needed_libraries")
            for engine, value in response.items():
                try:
                    if the_requirements_path is not None:
                        with self.localimport(the_requirements_path) as _importer:
                            response = self.decrypt(
                                encryption_key,
                                value,
                                engine,
                                try_to_extract_importable=try_to_extract_importable,
                            )
                            break
                    else:
                        response = self.decrypt(
                            encryption_key,
                            value,
                            engine,
                            try_to_extract_importable=try_to_extract_importable,
                        )
                        break
                except:
                    response = "Error"
                    self._log(f"Error on {engine} while loading {key}")
                    traceback.print_exc()
        except:
            if print_exc:
                if self.tester:
                    traceback.print_exc()
            else:
                pass

        # Run anayses
        if self.enable_usage_analyses and not pass_usage_analyses:
            if inspect.isfunction(response) and self.is_usage_analyses_true(key):
                commit = None
                if version == None:
                    the_dump_history = self.get_dump_history(key)
                    if len(the_dump_history) > 0:
                        commit = the_dump_history[0].split(":")[1]
                response = self.profile_function(key, version, commit, response)

        return response

    def os_name(self):
        system_name = platform.system()
        if system_name == "Windows":
            return "Windows"
        elif system_name == "Darwin":
            return "macOS"
        elif system_name == "Linux":
            return "Linux"
        else:
            return "Unknown OS"

    def add_run_history(
        self,
        key,
        version,
        cpu_usage_one_core,
        memory_usage,
        elapsed_time,
        type,
        params,
        exception_log,
    ):
        data = {
            "scope": key,
            "version": version,
            "cpu_usage": cpu_usage_one_core,
            "memory_usage": memory_usage,
            "elapsed_time": elapsed_time,
            "type": type,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "os_name": self.os_name(),
            "params": json.dumps(params),
            "exception_log": exception_log,
        }

        self._send_request("POST", "/dump_run", data)

    def get_dump_history(self, key):
        data = {"scope": key}
        return self._send_request("POST", "/get_dump_history", data)

    def profile_function(self, key, version, commit, func):
        @wraps(func)
        def wrapper_function(*args, **kwargs):
            # Get current process time and memory usage before function execution
            start_time = time.process_time()
            start_memory = memory_usage(-1, interval=0.1, timeout=1)[0]
            # Run the function and get its output
            succed = True
            try:
                output = func(*args, **kwargs)
            except:
                traceback.print_exc()
                succed = False
                output = traceback.format_exc()
            # Get process time and memory usage after function execution
            end_time = time.process_time()
            end_memory = memory_usage(-1, interval=0.1, timeout=1)[0]
            # Calculate time used and memory used
            time_used = end_time - start_time
            memory_used = end_memory - start_memory
            # Calculate the total CPU time available
            total_time = time_used

            cpu_usage_for_one_core = time_used * 100

            def is_basic_type(value):
                """Check if the value is of a basic type (int, float, str, list, dict)."""
                if isinstance(value, (int, float, str)):
                    return True
                elif isinstance(value, list):
                    return all(is_basic_type(item) for item in value)
                elif isinstance(value, dict):
                    return all(
                        is_basic_type(k) and is_basic_type(v) for k, v in value.items()
                    )
                return False

            def normalize_params(*args, **kwargs):
                """Normalize *args and **kwargs into a dictionary with only basic types."""
                normalized = {}

                # Normalize args
                for i, arg in enumerate(args):
                    if is_basic_type(arg):
                        normalized[f"arg_{i}"] = arg

                # Normalize kwargs
                for key, value in kwargs.items():
                    if is_basic_type(value):
                        normalized[key] = value

                return normalized

            the_params = normalize_params(*args, **kwargs)

            the_version = None
            if version == None:
                latest_commit = commit
                the_version = latest_commit
            else:
                the_version = version
            the_type = "Succed" if succed else "Failed"
            exception_log = None
            if not succed:
                exception_log = output
            try:
                self.add_run_history(
                    key,
                    the_version,
                    cpu_usage_for_one_core,
                    memory_used,
                    total_time,
                    the_type,
                    the_params,
                    exception_log,
                )
            except:
                self._log(
                    f"Error on adding run history, for server not supported. {key}"
                )
            return output

        return wrapper_function

    def get_settings(self, key):
        data = {"scope": key}
        return self._send_request("POST", "/get_settings_of_scope", data)

    def is_usage_analyses_true(self, key):
        settings = self.get_settings(key)

        if settings == None or settings == [None]:
            cpu_usage_analyses = False
        else:
            if "usage_analyses" in settings:
                try:
                    cpu_usage_analyses = settings["usage_analyses"].lower() == "true"
                except:
                    cpu_usage_analyses = None

        return cpu_usage_analyses

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

    def get_all(
        self,
    ):
        encryption_key = "u"

        datas = self._send_request("GET", "/get_all_scopes_user")
        return datas

    def delete(self, scope):
        data = {"scope": scope}
        return self._send_request("POST", "/delete_scope", data)

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

    def ai_completion(self, message, model=None):
        data = {"message": message}
        if model != None:
            data["model"] = model
        return self._send_request("POST", "/ai_completion", data)

    def get_all_scopes_user(self):
        return self._send_request("GET", "/get_all_scopes_user")



    def auto_dump(
        self, value, ask=True, check_function=True, print_prompts=False, model=None
    ):
        if model == None:
            model = self.get_default_ai_model()

        if model == "llama3-8b":
            check_function = False

        if check_function:
            check = self.check_function(value, print_prompts=print_prompts, model=model)
            if check != True:
                print("Check:", check)
                return

        code = textwrap.dedent(extract_source(value))
        all_scopes = self.get_all_scopes_user()
        all_scopes = "\n".join(all_scopes)

        prompt = f"""
You are an helpful software engineer. Help to organize library elements in a short and clear manner.


Generate a position for this:
```
{code}
```

Currenlty Index of Library:
```
{all_scopes}
```

Your answer should be just the suggested position. Dont say any other think.


Suggested Position:

"""

        ai_answer = self.ai_completion(prompt, model=model)
        ai_answer = ai_answer.replace("`", "").replace("\n", "")
        ai_answer = ".".join(ai_answer.split(".")[:-1])
        ai_answer = ai_answer + "." + dill.source.getname(value)
        prompt = prompt + f"\nASSISTANT: {ai_answer}\n"

        prompt = (
            prompt + "\nQUESTION: Extract and just answer with the suggested position"
        )
        if print_prompts:
            print(
                "Prompt", prompt.replace(code, "CODE").replace(all_scopes, "ALL SCOPES")
            )
        ai_answer = self.ai_completion(prompt, model=model)
        if print_prompts:
            print(
                "AI answer",
                ai_answer.replace(code, "CODE").replace(all_scopes, "ALL SCOPES"),
            )
        ai_answer = ai_answer.replace("`", "").replace("\n", "")
        ai_answer = ai_answer.replace("ASSISTANT: ", "")
        if ai_answer in all_scopes:
            print(f"Check: similarity with the {ai_answer} is detected")
            return
        if ask:
            print("Commands:\n(Y)es/(N)o\n")
            while True:
                y_n = input(f"{ai_answer} ").lower()

                if y_n == "y":
                    self.set(ai_answer, value)
                    print("\nDumped")
                    break
                if y_n == "n":
                    break

        else:
            self.set(ai_answer, value)
            print("\nDumped")

    def get_code(self, scope):
        data = {"scope": scope}
        return self._send_request("POST", "/get_code_of_scope", data)

    def get_document(self, scope, version=None):
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return self._send_request("POST", "/get_document_of_scope", data)

    def check_function(self, value, print_prompts=False, model=None):
        code = textwrap.dedent(extract_source(value))

        all_scopes_ = self.get_all_scopes_user()
        all_scopes = ""
        for i in all_scopes_:
            all_scopes += i + "\n"

        if print_prompts:
            print("Code", code)
            print("All scopes", all_scopes)

        prompt = f"""
Current Library Index:
```
{all_scopes}

```

Now analyze the each element of Current Library Index, if you want a potential similar functionality with this:

```
{code}

```

Which one is the most similar ?
"""

        ai_answer = self.ai_completion(prompt, model=model)

        ai_answer = ai_answer.replace("`", "").replace("\n", "")

        similarity_explanation = ai_answer

        prompt = prompt + f"\nASSISTANT: {ai_answer}\n"

        prompt = prompt + "\nQUESTION: Is there any duplication risk (Y/N)?"

        if print_prompts:
            print(
                "Prompt", prompt.replace(code, "CODE").replace(all_scopes, "ALL SCOPES")
            )
        ai_answer = self.ai_completion(prompt, model=model)
        ai_answer = ai_answer.replace("`", "").replace("\n", "")
        ai_answer = ai_answer.split(",")[0]
        ai_answer = ai_answer.replace("ASSISTANT: ", "")
        if print_prompts:
            print(
                "AI answer",
                ai_answer.replace(code, "CODE").replace(all_scopes, "ALL SCOPES"),
            )
        if ai_answer == "Y" or ai_answer == "YES" or ai_answer == "Yes":
            prompt = prompt + f"\nASSISTANT: {ai_answer}\n"

            prompt = (
                prompt
                + "\nQUESTION: Extract and just answer with the suggested position"
            )
            ai_answer = self.ai_completion(prompt, model=model)
            ai_answer = ai_answer.replace("`", "").replace("\n", "")
            ai_answer = ai_answer.split(",")[0]
            ai_answer = ai_answer.replace("ASSISTANT: ", "")
            return "similarity: " + ai_answer + " - " + similarity_explanation
        if ai_answer == "N" or ai_answer == "NO" or ai_answer == "No":
            return True
        return similarity_explanation

    def search_by_documentation(self, question):
        data = {"question": question}
        response = self._send_request("POST", "/search_by_documentation", data)
        result = []
        for i in response:
            result.append(i[0])
        return result

    def search(self, question):
        return self.search_by_documentation(question)

    def get_default_ai_model(self):
        return self._send_request("GET", "/get_default_ai_model")

    def get_version_history(self, key):
        data = {"scope": key}
        version = self._send_request("POST", "/get_version_history", data)
        return version

    def get_module_version_history(self, key):
        data = {"top_library": key}
        return self._send_request("POST", "/get_module_version_history", data)

    def delete_version(self, key, version):
        data = {"version": key + ":" + version}
        return self._send_request("POST", "/delete_version", data)

    def delete_module_version(self, module_name, version):
        data = {"top_library": module_name, "version": version}
        return self._send_request("POST", "/delete_version_prefix", data)

    def create_version(self, key, version):
        data = {"scope": key, "version": version}
        return self._send_request("POST", "/create_version", data)

    def create_module_version(self, module_name, version):
        data = {"top_library": module_name, "version": version}
        return self._send_request("POST", "/create_version_prefix", data)

    def get_version_data(self, key, version):
        data = {"version": key + ":" + version}
        return self._send_request("POST", "/load_specific_version", data)

    def get_requirements(self, key):
        data = {"scope": key}
        return self._send_request("POST", "/get_requirements_of_scope", data)

    def add_requirement(self, key, requirement):
        currently_requirements = self.get_requirements(key)
        if currently_requirements == None:
            currently_requirements = ""

        if currently_requirements != "":
            currently_requirements += ", "

        currently_requirements += requirement
        data = {
            "scope": key,
            "requirements": currently_requirements,
        }
        return self._send_request("POST", "/dump_requirements", data)

    def clear_requirements(self, key):
        data = {
            "scope": key,
            "requirements": "",
        }
        return self._send_request("POST", "/dump_requirements", data)

    def get_type(self, key, version=None):
        data = {"scope": key}
        if version != None:
            data["version"] = version
        return self._send_request("POST", "/get_type_of_scope", data)

    def get_code(self, key, version=None):
        data = {"scope": key}
        if version != None:
            data["version"] = version
        return self._send_request("POST", "/get_code_of_scope", data)

    def langchain(self, prefix=None, version=None):
        from langchain.tools import tool

        all_functions = []
        for each in self.get_all():
            if each.endswith("__user"):
                continue
            the_true_name = each
            the_true_name = the_true_name.replace("_", ".")
            the_true_name = the_true_name.replace(".", "_")
            if prefix != None:
                if not each.startswith(prefix):
                    continue
            if self.get_type(each) == "function":
                the_function = self.get(each, version=version)
                if inspect.isfunction(the_function):
                    the_document = self.get_document(each, version=version) or " "
                    the_function.__doc__ = the_document
                    try:
                        the_tool = tool(the_function)
                        original_name = the_tool.name
                        the_tool.name = the_true_name
                        the_tool.description = the_tool.description.replace(
                            original_name, the_true_name
                        )[:1000]
                        all_functions.append(the_tool)
                    except:
                        traceback.print_exc()
                        pass
        return all_functions

    def crewai(self, prefix=None, version=None):
        from crewai_tools import tool

        all_functions = []
        for each in self.get_all():
            if each.endswith("__user"):
                continue
            the_true_name = each
            the_true_name = the_true_name.replace("_", ".")
            the_true_name = the_true_name.replace(".", "_")
            if prefix != None:
                if not each.startswith(prefix):
                    continue
            if self.get_type(each) == "function":
                the_function = self.get(each, version=version)
                if inspect.isfunction(the_function):
                    the_document = self.get_document(each, version=version) or " "
                    the_function.__doc__ = the_document
                    try:
                        the_tool = tool(the_function)
                        original_name = the_tool.name
                        the_tool.name = the_true_name
                        the_tool.description = the_tool.description.replace(
                            original_name, the_true_name
                        )[:1000]
                        all_functions.append(the_tool)
                    except:
                        traceback.print_exc()
                        pass
        return all_functions

    def autogen(self, caller, executor, prefix=None, version=None):
        import autogen

        for each in self.get_all():
            if each.endswith("__user"):
                continue
            the_true_name = each
            the_true_name = the_true_name.replace("_", ".")
            the_true_name = the_true_name.replace(".", "_")
            if prefix != None:
                if not each.startswith(prefix):
                    continue
            if self.get_type(each) == "function":
                the_function = self.get(each, version=version)
                if inspect.isfunction(the_function):
                    the_document = self.get_document(each, version=version) or " "
                    the_function.__doc__ = the_document
                    try:
                        the_document = the_document.replace(
                            each, the_true_name
                        ).replace(each.split(".")[-1], the_true_name)[:1000]
                        autogen.agentchat.register_function(
                            the_function,
                            caller=caller,
                            executor=executor,
                            description=the_document,
                            name=the_true_name,
                        )
                    except:
                        traceback.print_exc()
                        pass

    def openinterpreter(self, agent, prefix=None, version=None):
        def replace_function_name(input_string, new_function_name):
            result = re.sub(
                r"^(def )(\w+)",
                f"\g<1>{new_function_name}",
                input_string,
                flags=re.MULTILINE,
            )
            return result

        def extract_function_definition(input_string):
            function_name = input_string.split("def ")[1].split(")")[0]

            return function_name + ")"

        class open_interpreter_tool:
            def __init__(self, function, name, document):
                self.name = name
                self.description = document
                self.function = replace_function_name(function, name)

            @property
            def type_for_prompt(self):
                the_description = self.description[:200]
                the_description.replace("\n", " ")
                return (
                    extract_function_definition(self.function).replace("\n", " ")
                    + " #"
                    + the_description
                )

        all_functions = []
        for each in self.get_all():
            if each.endswith("__user"):
                continue
            the_true_name = each
            original_name = each
            the_true_name = the_true_name.replace("_", ".")
            the_true_name = the_true_name.replace(".", "_")
            if prefix != None:
                if not each.startswith(prefix):
                    continue
            if self.get_type(each) == "function":
                the_function = self.get(
                    each, version=version, try_to_extract_importable=True
                )
                the_document = self.get_document(each, version=version) or " "
                the_document = the_document.replace(
                    original_name.split(".")[-1], the_true_name
                )[:1000]
                try:
                    the_tool = open_interpreter_tool(
                        the_function, the_true_name, the_document
                    )
                    all_functions.append(the_tool)
                except:
                    traceback.print_exc()
                    pass

        for each_f in all_functions:
            if self.tester:
                self._log(each_f.function)
            agent.computer.run("python", each_f.function)

        agent.system_message += r"""
# THE OTHER APIs
    
These functions ALREADY IMPORTED, and can be used for many tasks:
    
```python
    
    """

        for each_f in all_functions:
            agent.system_message += each_f.type_for_prompt + "\n\n"

        agent.system_message += r"""
```
    
Do not import the anythink, They are already imported.
    """

    def return_openai_llm(self, model=None):
        from langchain_openai import ChatOpenAI
        import httpx

        httpx_client = httpx.Client(verify=False)

        llm = ChatOpenAI(
            openai_api_key=self.password,
            http_client=httpx_client,
            openai_api_base=self.api_url + "/openai/",
            model_name=model,
        )
        return llm

    def return_ollama_llm(self, model=None):
        from .ollama_langchain import Ollama

        llm = Ollama(
            model=f"{model}**{self.password}", base_url=self.api_url + "/ollama"
        )
        return llm

    def check_idea(self, idea):
        search_result = self.search(idea)
        if len(search_result) == 0:
            return True

        # Get the first result of check and as ai to check the similarity
        first_result = search_result[0]

        # Get the document of the first result
        first_result_document = self.get_document(first_result)

        # get the code of the first result
        first_result_code = self.get_code(first_result)

        # Ask to AI to check the similarity
        prompt = f"""
        The user planning to write a function about this: {idea}

        Currently function: {first_result}
        Currently function Document: {first_result_document}
        Currently function Code: {first_result_code}

        Is the idea making same thing with the first result (Y/N)?
        """

        ai_answer = self.ai_completion(prompt)
        ai_answer = ai_answer.replace("`", "").replace("\n", "")
        ai_answer = ai_answer.split(",")[0]
        ai_answer = ai_answer.replace("ASSISTANT: ", "")

        is_not_similar = False

        if ai_answer == "N" or ai_answer == "NO" or ai_answer == "No":
            is_not_similar = True

        if not is_not_similar:
            # Ask ai to explain similarity in one sentence
            prompt = f"""
            Current Idea: {idea}
            First Result: {first_result}
            First Result Document: {first_result_document}
            First Result Code: {first_result_code}

            Explain the similarity in one sentence. If you need to refer to First Result please use {first_result}.
            """

            ai_answer = self.ai_completion(prompt)
            ai_answer = ai_answer.replace("`", "").replace("\n", "")
            ai_answer = ai_answer.split(",")[0]
            ai_answer = ai_answer.replace("ASSISTANT: ", "")

            return "Fail: " + ai_answer
        else:
            return "Pass: There is no same functionality in the library"


class UpsonicOnPrem(Upsonic_On_Prem):
    pass


def Tiger():
    return Upsonic_On_Prem(
        "https://api_tiger.upsonic.co",
        "ACK_xmxIiqsgGySvBPPd55M0Ldm5AcR2kt6r3kmL52Ptqo",
        engine="upsonic_serializer",
        pass_python_version_check=True,
        enable_auto_requirements=True,
    )


def Tiger_Admin(api_url, access_key):
    return Upsonic_On_Prem(
        api_url,
        access_key,
        engine="upsonic_serializer",
        pass_python_version_check=True,
        enable_auto_requirements=True,
    )
