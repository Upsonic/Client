import traceback

try:
    from .core import Upsonic
    from .core import start_location
    from .core import HASHES
    from .core import Upsonic_Serial

except:
    pass

from .remote import Upsonic_Remote
from .remote import Upsonic_Cloud_Free
from .remote import Upsonic_Cloud_Pro
from .remote import Upsonic_Cloud_Premium
from .remote import Upsonic_Cloud_Startup
from .remote import Upsonic_Cloud_Readonly
from .remote import no_exception
from .remote import requires
from .remote import encrypt
from .remote import decrypt

from rich.console import Console

console = Console()

open_databases = {}

__version__ = '0.8.3'



