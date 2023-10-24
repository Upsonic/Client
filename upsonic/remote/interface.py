#!/usr/bin/python3
# -*- coding: utf-8 -*-



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



def Upsonic_Cloud_Free(database_name, access_key):
    from upsonic import Upsonic_Remote
    return Upsonic_Remote(
        database_name, "https://cloud_1.upsonic.co", access_key, verify=True
    )  # pragma: no cover


def Upsonic_Cloud_Pro(database_name, access_key):
    from upsonic import Upsonic_Remote
    return Upsonic_Remote(
        database_name, "https://cloud_2.upsonic.co", access_key, verify=True
    )  # pragma: no cover


def Upsonic_Cloud_Premium(database_name, access_key):
    from upsonic import Upsonic_Remote
    return Upsonic_Remote(
        database_name, "https://cloud_3.upsonic.co", access_key, verify=True
    )  # pragma: no cover



def Upsonic_Cloud_Readonly(database_name, access_key):
    from upsonic import Upsonic_Remote
    return Upsonic_Remote(
        database_name, "https://cloud_0.upsonic.co", access_key, verify=True
    )  # pragma: no cover