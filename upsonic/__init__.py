import traceback



import warnings
# Suppress the deprecation warning from the cryptography module.
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import cryptography


try:
    from .core import Upsonic
    from .core import start_location
    from .core import HASHES
    from .core import Upsonic_Serial

except:
    pass

from .remote import localimport
from .remote import Upsonic_On_Prem, Tiger, Tiger_Admin, UpsonicOnPrem
from .remote import no_exception
from .remote import requires
from .remote import encrypt
from .remote import decrypt
from .remote import upsonic_serializer
from .remote import interface


open_databases = {}

__version__ = '0.34.3'  # fmt: skip
