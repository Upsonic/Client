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
import sys

from pip._internal.operations import freeze

import traceback

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

    def __init__(self, api_url, access_key, engine="cloudpickle", byref=True, recurse=True, protocol=pickle.DEFAULT_PROTOCOL, source=True, builtin=True):
        import requests
        from requests.auth import HTTPBasicAuth

        from requests.packages.urllib3.exceptions import InsecureRequestWarning

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


        from upsonic import console

        self.console = console

        self.requests = requests
        self.HTTPBasicAuth = HTTPBasicAuth

        self.api_url = api_url
        self.password = access_key
        self.engine=engine
        self.byref=byref
        self.recurse=recurse
        self.protocol = protocol
        self.source = source
        self.builtin = builtin

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


    def load_module(self, module_name, version=None):
        encryption_key = "u"
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
                if version != None:
                    version_list_response = self.get_version_history(original_i)
                    version_list = []
                    for each_v in version_list_response:
                        version_list.append(each_v.replace(original_i+":", ""))
                    if version in version_list:
                        try:
                            the_all_imports[i] = self.get(
                                original_i,
                                version,
                            )
                        except:
                            the_all_imports[i] = self.get(original_i)
                else:
                    the_all_imports[i] = self.get(original_i,)
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
            version=None
    ):
        return self.get(
            key,
            version=version,
            print_exc=True
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

        data = {
            "scope": key,
            "code": textwrap.dedent(self.extract_source(value)),
        }

        self._send_request("POST", "/dump_code", data)





        data = {"scope": key, "type": the_type}

        self._send_request("POST", "/dump_type", data)


        data = {
            "scope": key,
            "requirements": Upsonic_On_Prem.export_requirement(),
        }

        self._send_request("POST", "/dump_requirements", data)



        data = {
            "scope": key,
            "python_version": sys.version,
        }

        self._send_request("POST", "/dump_python_version", data)


        data = {
            "scope": key,
            "data": self.encrypt(encryption_key, value, self.engine, self.byref, self.recurse, self.protocol, self.source, self.builtin)
        }

        self._send_request("POST", "/dump", data)


        return True

    def get(
            self,
            key,
            version=None,
            print_exc=True

    ):
        response = None

        encryption_key = "u"

        data = {"scope": key}

        if response is None:
            if version != None:
                response = self.get_version_data(key, version)
            else:
                response = self._send_request("POST", "/load", data)
        try:
            response = self.decrypt(encryption_key, response, self.engine)
        except:
            if print_exc:
                self._log(f"Error on {key} please use same python versions")
            else:
                pass
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


    def extract_source(self, value):
        result = ""
        try:
            result = inspect.getsource(value)
        except:
            result = dill.source.getsource(value)
        return result


    def auto_dump(self, value, ask=True, check_idea=True, print_prompts=False, model=None):
        if check_idea:
            check = self.check_idea(value, print_prompts=print_prompts, model=model)
            if check != True:
                print("Check:", check)
                return

        code = textwrap.dedent(self.extract_source(value))
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

Suggested Position:

"""

        ai_answer = self.ai_completion(prompt, model=model)
        ai_answer = ai_answer.replace("`", "").replace("\n", "")
        ai_answer = '.'.join(ai_answer.split('.')[:-1])
        ai_answer = ai_answer + "." + dill.source.getname(value)
        prompt = prompt + f"\nASSISTANT: {ai_answer}\n"

        prompt = prompt + f"\nQUESTION: Extract and just answer with the suggested position"
        if print_prompts:
            print("Prompt", prompt.replace(code, "CODE").replace(all_scopes, "ALL SCOPES"))
        ai_answer = self.ai_completion(prompt, model=model)
        if print_prompts:
            print("AI answer", ai_answer.replace(code, "CODE").replace(all_scopes, "ALL SCOPES"))
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

    def get_document(self, scope):
        data = {"scope": scope}
        return self._send_request("POST", "/get_document_of_scope", data)


    def check_idea(self, value, print_prompts=False, model=None):
        code = textwrap.dedent(self.extract_source(value))


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

        prompt = prompt + f"\nQUESTION: Is there any duplication risk (Y/N)?"


        if print_prompts:
            print("Prompt", prompt.replace(code, "CODE").replace(all_scopes, "ALL SCOPES"))
        ai_answer = self.ai_completion(prompt, model=model)
        ai_answer = ai_answer.replace("`", "").replace("\n", "")
        ai_answer = ai_answer.split(",")[0]
        ai_answer = ai_answer.replace("ASSISTANT: ", "")
        if print_prompts:
            print("AI answer", ai_answer.replace(code, "CODE").replace(all_scopes, "ALL SCOPES"))
        if ai_answer == "Y" or ai_answer == "YES" or ai_answer == "Yes":
            prompt = prompt + f"\nASSISTANT: {ai_answer}\n"

            prompt = prompt + f"\nQUESTION: Extract and just answer with the suggested position"
            ai_answer = self.ai_completion(prompt, model=model)
            ai_answer = ai_answer.replace("`", "").replace("\n", "")
            ai_answer = ai_answer.split(",")[0]
            ai_answer = ai_answer.replace("ASSISTANT: ", "")
            return "similarity: "+ai_answer + " - " + similarity_explanation
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
        return self._send_request("POST", "/get_version_history", data)

    def get_module_version_history(self, key):
        data = {"top_library": key}
        return self._send_request("POST", "/get_module_version_history", data)


    def delete_version(self, key, version):
        data = {"version": key+":"+version}
        return self._send_request("POST", "/delete_version", data)

    def delete_module_version(self, module_name, version):
        data = {"top_library":module_name ,"version": version}
        return self._send_request("POST", "/delete_version_prefix", data)

    def create_version(self, key, version):
        data = {"scope":key ,"version": version}
        return self._send_request("POST", "/create_version", data)


    def create_module_version(self, module_name, version):
        data = {"top_library":module_name ,"version": version}
        return self._send_request("POST", "/create_version_prefix", data)




    def get_version_data(self, key, version):
        data = {"version": key+":"+version}
        return self._send_request("POST", "/load_specific_version", data)