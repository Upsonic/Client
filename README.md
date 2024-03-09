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


## Advisors



<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><img src="https://github.com/Upsonic/Upsonic/assets/41792982/b4f4ad18-796e-46ce-9c5a-a50ebaf7f2fe" width="100px;" alt="Bugra Kocaturk"/><br /><b>Buğra Kocatürk</b><br /> <sub>AWS Solution Architect </sub><br /><br /> AWS Netherlands <br /><a href="https://www.linkedin.com/in/bugrakocaturk/" title="Linkedin">Linkedin</a></td>
      <td align="center" valign="top" width="14.28%"><img src="https://github.com/Upsonic/Upsonic/assets/41792982/99307f93-4841-4abb-8ae0-e5e25c75e840" width="100px;" alt="Lemi Orhan Engin"/><br /><b>Lemi Orhan Engin</b><br /> <sub>CTO </sub><br /><br /> Craftgate <br /><a href="https://www.linkedin.com/in/lemiorhan/" title="Linkedin">Linkedin</a></td>
      <td align="center" valign="top" width="14.28%"><img src="https://github.com/Upsonic/Upsonic/assets/41792982/f47a040c-3d38-4965-82ac-27ee064cb501" width="100px;" alt="Mehmet Emin Ozturk"/><br /><b>Mehmet Emin Öztürk</b><br /> <sub>Data Team Lead & Kaggle Master  </sub><br /> Trendyol Group <br /><a href="https://www.linkedin.com/in/meminozturk/" title="Linkedin">Linkedin</a></td>
      <td align="center" valign="top" width="14.28%"><img src="https://github.com/Upsonic/Upsonic/assets/41792982/82388171-1bd8-460c-b7f2-322f94b13707" width="100px;" alt="Firat Gonen"/><br /><b>Fırat Gönen</b><br /> <sub>Chief data Officer & Kaggle Grandmaster 3X </sub><br /> Figopara <br /><a href="https://www.linkedin.com/in/ffgonen/" title="Linkedin">Linkedin</a></td>      
    </tr>

    
  </tbody>
</table>


## Customers



<table>
   <tr>
      <td><a href="https://wears.com.tr/" target="_blank"><img src="https://github.com/Upsonic/Upsonic/assets/41792982/19f39eec-5251-45ce-837b-8e9db1df17ad" alt="wears" width = 360px></a></td>
       <td><a href="https://exar.com.tr/" target="_blank"><img src="https://github.com/Upsonic/Upsonic/assets/41792982/cf7d9753-97dc-4b9d-9847-4807fdbdd0e3" alt="exar" width = 360px></a></td>
             <td><a href="https://www.smartopt.com.tr/" target="_blank"><img src="https://github.com/Upsonic/Upsonic/assets/41792982/10d78a0e-65ae-424a-a8bd-d55cd7692223" alt="smartopt" width = 360px></a></td>
  </tr>
</table>
