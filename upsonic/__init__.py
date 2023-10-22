import traceback

try:
    from .core import Upsonic
    from .core import start_location
    from .core import HASHES
    from .core import Upsonic_Serial

except:
    traceback.print_exc()

from .remote import Upsonic_Remote
from .remote import Upsonic_Cloud
from .remote import Upsonic_Cloud_Pro
from .remote import Upsonic_Cloud_Dedicated
from .remote import Upsonic_Cloud_Dedicated_Prepare
from .remote import no_exception
from .remote import requires
from .remote import encrypt
from .remote import decrypt

from rich.console import Console

console = Console()

open_databases = {}

__version__ = '0.4.11'


