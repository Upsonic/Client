#!/usr/bin/python3
# -*- coding: utf-8 -*-
from functools import wraps


def no_exception(func):
    @wraps(func)
    def runner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            print(f"Exception occurred in function: {e}")

    return runner


@no_exception
def requires(name, custom_import=None):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                import_name = name if custom_import is None else custom_import
                exec(f"import {import_name}")
            except:
                from pip._internal import main as pip

                pip(["install", name])
            retval = function(*args, **kwargs)
            return retval

        return wrapper

    return decorator


"""

def durable(func):
    @wraps(func)
    def runner(*args, **kwargs):
        import random
        result = None
        run_id = random.randint(10000, 99999)
        while result is None:
            try:
                result = func(*args, **kwargs)
       
            except Exception as e:
                import time
                print(f"Exception occurred in function and frozed the statement, waiting for update: {e}")
                cloud.set(func.__name__+"_upsonic_durable"+str(run_id), str(e))
                time.sleep(5)
        return result
    return runner

"""
