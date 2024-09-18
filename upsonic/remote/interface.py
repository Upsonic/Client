#!/usr/bin/python3
# -*- coding: utf-8 -*-


from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
import os


import cloudpickle
import dill
import pickle
import importlib.util


def upsonic_serializer(func):
    the_source = dill.source.findsource(func)
    the_full_string = ""
    for each in the_source[0]:
        the_full_string += each
    imports = [
        line + "\n"
        for line in the_full_string.split("\n")
        if line.startswith("import ") or line.startswith("from ")
    ]

    the_import_string = ""
    for each in imports:
        the_import_string += each

    the_function_string = dill.source.getsource(func)

    return the_import_string + "\n" + the_function_string


def encrypt(key, message, engine, byref, recurse, protocol, source, builtin):
    from cryptography.fernet import Fernet
    import base64
    import hashlib

    fernet_key = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest())
    fernet = Fernet(fernet_key)

    dumped = None
    if engine == "cloudpickle":
        the_module = dill.detect.getmodule(message)
        if the_module is not None:
            cloudpickle.register_pickle_by_value(the_module)
        dumped = cloudpickle.dumps(message, protocol=protocol)
    elif engine == "dill":
        dumped = dill.dumps(message, protocol=protocol, byref=byref, recurse=recurse)
    elif engine == "upsonic_serializer":
        name_of_object = dill.source.getname(message)

        if name_of_object == None:
            try:
                name_of_object = message.__name__
            except:
                pass

        dumped = {
            "name": name_of_object,
            "upsonic_serializer": upsonic_serializer(message),
        }
        dumped = pickle.dumps(dumped, protocol=1)

    encrypted_message = fernet.encrypt(dumped)
    return encrypted_message


def decrypt(key, message, engine, try_to_extract_importable=False):
    from cryptography.fernet import Fernet
    import base64
    import hashlib

    fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest()))

    loaded = None
    if engine == "cloudpickle":
        loaded = cloudpickle.loads(fernet.decrypt(message))
    elif engine == "dill":
        loaded = dill.loads(fernet.decrypt(message))
    elif engine == "upsonic_serializer":
        loaded = pickle.loads(fernet.decrypt(message))

        if try_to_extract_importable:
            return loaded["upsonic_serializer"]

        def extract(code_string, function_name):
            tmp_dir = os.path.dirname(os.path.abspath(__file__))
            tmp_file = os.path.join(tmp_dir, function_name + "_upsonic" + ".py")
            with open(tmp_file, "w") as f:
                f.write(code_string)

            spec = importlib.util.spec_from_file_location(
                function_name + "_upsonic", tmp_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            os.remove(tmp_file)  # Clean up the temporary file

            return getattr(module, function_name)

        loaded = extract(loaded["upsonic_serializer"], loaded["name"])

    return loaded

