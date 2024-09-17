import traceback

try:
    from .core import Upsonic
    from .core import start_location
    from .core import HASHES
    from .core import Upsonic_Serial

except:
    pass

from .remote import localimport
from .remote import Upsonic_Remote
from .remote import Upsonic_On_Prem, Tiger, Tiger_Admin, UpsonicOnPrem
from .remote import Upsonic_Cloud_Free
from .remote import Upsonic_Cloud_Pro
from .remote import Upsonic_Cloud_Premium
from .remote import Upsonic_Cloud_Startup
from .remote import Upsonic_Cloud_Readonly
from .remote import Upsonic_Cloud_Generic
from .remote import no_exception
from .remote import requires
from .remote import encrypt
from .remote import decrypt
from .remote import upsonic_serializer
from .remote import interface


open_databases = {}

__version__ = '0.30.0'  # fmt: skip
