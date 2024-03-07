# Upsonic | Python Client Library

The Upsonic Python Client Library is designed to help data scientists and ML engineers efficiently manage and automate maintenance-free utility library creation. It provides a simple, easy-to-use Python interface to interact with the Upsonic platform.
[Website](https://upsonic.co/) | [Discord](https://discord.gg/) | [Twitter](https://twitter.com/upsonicco)



## Features

- Easy serialization of functions and classes, making them readily available for reuse across different projects.
- Automatic documentation generation for effortless maintenance and readability.
- Support for both direct and modular function importation from the library.
- Streamlined version control and collaboration features, allowing teams to work together seamlessly.


  
## Installation

You need to install the Upsonic container.

Once the container is up and running, you can install the Upsonic Python Client Library on your local system using the pip package manager:
```console
# pip install upsonic
```



## Usage

Here's an updated quickstart guide to get you up and running with your container:

```python

# Import the Upsonic client
from upsonic import Upsonic_On_Prem

# Initialize the client by providing the Upsonic container URL and AccessKey
upsonic = Upsonic_On_Prem('https://your-server-address:5000', 'ACK_****************')

# This is assuming your Upsonic container is running locally on port 5000.

# Dump a function into the library
def sum(a, b):
    return a + b
dump("math.basics.sum", sum)

# Load a module or a function from the library
math = client.load_module("math")

math.basics.sum(5, 2)

```



## Documentation

You can find detailed documentation, including advanced usage and API reference, in the official [Upsonic Documentation](https://docs.upsonic.co/home) .



## Contributing

We welcome contributions to the Upsonic Python Client Library! 



## Support & Questions

For any questions or if you encounter an issue, please reach out to our support team at info@upsonic.co or open an issue on the project's GitHub page.



## License
Upsonic is released under the MIT License.

We hope you enjoy using Upsonic to streamline your utility library creation process, and we look forward to hearing your feedback and suggestions!
