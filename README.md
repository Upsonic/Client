# Upsonic | Self-Driven Autonomous Python Libraries

The Upsonic is designed to help data scientists and ML engineers efficiently manage and automate maintenance-free utility library creation. It provides a simple, easy-to-use Python interface to interact with the Upsonic platform.
[Website](https://upsonic.co/) | [Discord](https://discord.gg/) | [Twitter](https://twitter.com/upsonicco)



## Features

- Easy serialization of functions and classes, making them readily available for reuse across different projects.
- Automatic documentation generation for effortless maintenance and readability.
- Support for both direct and modular function importation from the library.
- Streamlined version control and collaboration features, allowing teams to work together seamlessly.

### Easiest Library View
Usponic proveides an dashboard for your team members. Everyone can access to the dashboard by their [user status](https://docs.upsonic.co/on-prem/using/users). After the accessing they can easily view the top libraries and automaticaly generated connections codes.
![image](https://github.com/Upsonic/Upsonic/assets/41792982/aa67f1f9-e510-4c5f-98fd-6876016157e7)


### Automaticaly Documentation
In Upsonic On-Prem dashboard we have automaticaly generated documentation for your each function, class, object or variables. For this you can use OpenAI GPT integration or a self-hosted Google Gemma model in your installation. They are making your documentations automaticaly. Also you can easily search your content.

- Documentation
- Time Complexity
- Mistakes
- Required Test Tyoes
- Security Analyses
- Tags

![image](https://github.com/Upsonic/Upsonic/assets/41792982/031678af-f0a4-43e9-976b-81707060e85e)

  
## Installation

You need to install the Upsonic container.

[Installing and Running On-Prem Container](https://docs.upsonic.co/on-prem/getting_started/install_on_prem)

Once the container is up and running, you can install the Upsonic Python Client Library on your local system using the pip package manager:
```console
# pip install upsonic
```



## Usage

Upsonic streamlines the development and deployment of utility libraries. Here's how to get started:

### Basic Usage

1. Initialize Upsonic with your server's address:
   ```python
   from upsonic import Upsonic_On_Prem
   upsonic = Upsonic_On_Prem('https://your-server-address:5000', 'ACK_****************')
   ```

2. Define a function you wish to serialize and share:
   ```python
   def sum(a, b):
       return a + b
   ```

3. Serialize the function for Upsonic:
   ```python
   upsonic.dump("math.basics.sum", sum)
   ```

4. Import and use the serialized function in another project:
   ```python
   math = upsonic.load_module("math")
   math.basics.sum(5, 2)
   ```

### Advanced Usage

For complex scenarios and advanced usage, refer to our [detailed documentation](https://docs.upsonic.co/home).

```python
from upsonic import Upsonic_On_Prem
upsonic = Upsonic_On_Prem('https://your-server-address:5000', 'ACK_****************')



def sum(a, b):
    return a + b

upsonic.dump("math.basics.sum", sum)



math = upsonic.load_module("math")

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
