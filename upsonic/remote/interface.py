#!/usr/bin/python3
# -*- coding: utf-8 -*-


from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")
import os




def encrypt(key, message):
    from cryptography.fernet import Fernet
    import base64
    import hashlib
    import dill
    fernet_key = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest())
    fernet = Fernet(fernet_key)
    encrypted_message = fernet.encrypt(dill.dumps(message))
    return encrypted_message

def decrypt(key, message):
    from cryptography.fernet import Fernet
    import base64
    import hashlib    
    import dill
    fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest()))
    decrypted_message = dill.loads(fernet.decrypt(message))
    return decrypted_message



def Upsonic_Cloud_Free(database_name=None, access_key=None, locking=None):
    if database_name == None:
        database_name = os.environ.get("database_Free")
    if access_key == None:
        access_key = os.environ.get("access_key_Free")


    if locking == None:
        locking = os.environ.get("locking", "false").lower() == "true"


    from upsonic import Upsonic_Remote
    return Upsonic_Remote(
        database_name, "https://cloud_1.upsonic.co", access_key, verify=True, locking=locking
    )  # pragma: no cover


def Upsonic_Cloud_Pro(database_name=None, access_key=None, locking=None):
    if database_name == None:
        database_name = os.environ.get("database_Pro")
    if access_key == None:
        access_key = os.environ.get("access_key_Pro")


    if locking == None:
        locking = os.environ.get("locking", "false").lower() == "true"

    from upsonic import Upsonic_Remote
    return Upsonic_Remote(
        database_name, "https://cloud_2.upsonic.co", access_key, verify=True, locking=locking
    )  # pragma: no cover


def Upsonic_Cloud_Premium(database_name=None, access_key=None, locking=None):
    if database_name == None:
        database_name = os.environ.get("database_Premium")
    if access_key == None:
        access_key = os.environ.get("access_key_Premium")

    if locking == None:
        locking = os.environ.get("locking", "false").lower() == "true"

    from upsonic import Upsonic_Remote
    return Upsonic_Remote(
        database_name, "https://cloud_3.upsonic.co", access_key, verify=True, locking=locking
    )  # pragma: no cover

def Upsonic_Cloud_Startup(database_name=None, access_key=None, locking=None):
    if database_name == None:
        database_name = os.environ.get("database_Startup")
    if access_key == None:
        access_key = os.environ.get("access_key_Startup")


    if locking == None:
        locking = os.environ.get("locking", "false").lower() == "true"

    from upsonic import Upsonic_Remote
    return Upsonic_Remote(
        database_name, "https://cloud_4.upsonic.co", access_key, verify=True, locking=locking
    )  # pragma: no cover




def Upsonic_Cloud_Readonly(database_name=None, access_key=None, locking=None):
    if database_name == None:
        database_name = os.environ.get("database_Readonly")
    if access_key == None:
        access_key = os.environ.get("access_key_Readonly")

    if locking == None:
        locking = os.environ.get("locking", "false").lower() == "true"


    from upsonic import Upsonic_Remote
    return Upsonic_Remote(
        database_name, "https://cloud_0.upsonic.co", access_key, verify=True, locking=locking
    )  # pragma: no cover




class _Upsonic_CLI:
    def __init__(self, type, database_name=None, access_key=None, locking=None) -> None:
        self.type = type


        if locking == None:
            self.locking = os.environ.get("locking", "false").lower() == "true"

        if self.type.lower() == "free":
            if database_name == None:
               database_name = os.environ.get("database_free")
            if access_key == None:
                access_key = os.environ.get("access_key_free")
            
            self.cloud = Upsonic_Cloud_Free(database_name, access_key, locking=self.locking)
        elif self.type.lower() == "pro":
            if database_name == None:
               database_name = os.environ.get("database_Pro")
            if access_key == None:
                access_key = os.environ.get("access_key_Pro")
            
            self.cloud = Upsonic_Cloud_Pro(database_name, access_key, locking=self.locking)

        elif self.type.lower() == "premium":
            if database_name == None:
               database_name = os.environ.get("database_Premium")
            if access_key == None:
                access_key = os.environ.get("access_key_Premium")
            
            self.cloud = Upsonic_Cloud_Premium(database_name, access_key, locking=self.locking)

        elif self.type.lower() == "startup":
            if database_name == None:
               database_name = os.environ.get("database_Startup")
            if access_key == None:
                access_key = os.environ.get("access_key_Startup")
            
            self.cloud = Upsonic_Cloud_Startup(database_name, access_key, locking=self.locking)

        elif self.type.lower() == "readonly":
            if database_name == None:
               database_name = os.environ.get("database_Readonly")
            if access_key == None:
                access_key = os.environ.get("access_key_Readonly")
            
            self.cloud = Upsonic_Cloud_Readonly(database_name, access_key, locking=self.locking)

        else:
            raise Exception("Invalid type")



    def lock(self, key):
        return self.cloud.lock_key(key)
        
    def unlock(self, key):
        return self.cloud.unlock_key(key)
               

def Upsonic_CLI():
    import fire
    fire.Fire(_Upsonic_CLI)