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



def Upsonic_Cloud(database_name):
    from upsonic import Upsonic_Remote
    return Upsonic_Remote(
        database_name, "https://cloud_1.upsonic.co", "onuratakan", verify=False
    )  # pragma: no cover


def Upsonic_Cloud_Pro(database_name, access_key):
    from upsonic import Upsonic_Remote
    return Upsonic_Remote(
        database_name, "https://cloud_2.upsonic.co", access_key, verify=False
    )  # pragma: no cover


def Upsonic_Cloud_Dedicated(database_name, password, dedicated_key):
    from upsonic import Upsonic_Remote
    dedicated_key = dedicated_key.replace("dedicatedkey-", "")
    dedicated_key = dedicated_key.encode()
    host = decrypt("dedicatedkey", dedicated_key)
    return Upsonic_Remote(database_name, host, password, verify=False)  # pragma: no cover


def Upsonic_Cloud_Dedicated_Prepare(host):
    host = encrypt("dedicatedkey", host)
    host = host.decode()
    host = "dedicatedkey-" + host
    return host
