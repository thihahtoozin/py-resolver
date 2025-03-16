# PyResolver – Python-based DNS resolver

**PyResolver** is the minimalist DNS implementation for the local network written in python. A simple, lightweight DNS server written in Python that can simply resolve domain names and support custom mappings. This project is designed for educational purposes, local network DNS resolution, or as a customizable alternative to public DNS resolvers.

## Introduction  

This project is a python-based DNS server running on udp protocol that can resolve domain names and return appropriate IP addresses based on predefined records. It is useful for:  
- Setting up a local DNS server for development or testing  
- Overriding domain resolutions for specific domains  
- Learning how DNS servers work  

## Features  

✔️ Only supports **A** record

✔️ **Custom domain mappings** using a configuration file  

✔️ Can run on **any port**, not just 53 (useful for testing)  

✔️ **Minimal dependencies** (uses Python’s built-in socket module)  

## Installation
Just install `python3` and clone this repository:
```
git clone https://github.com/thihahtoozin/py-resolver
```

### Requirements
- Python 3.13.2 or above is fine


## Configuration
You can have custom configurations by adding or modifying zone files in under `zones/` directory
```sh
vim zones/segfault.local.zone
```

Example of a zone file
```sh
$TTL 86400 ;
$ORIGIN segfault.local. ;
@   IN  SOA     ns1.segfault.local. hostmaster.segfault.local. (
            2024111401   ; Serial
            3600         ; Refresh
            1800         ; Retry
            1209600      ; Expire
            86400 )      ; Minimum TTL
@   IN  NS      ns1.segfault.local.
ns1 IN  A       192.168.100.254      ; Replace with your server IP
ssh IN	A	192.168.100.254      ; SSH Server
www IN  A       192.168.100.254      ; Example entry for a website host
```

## Usage
### Running DNS Server
```sh
sudo python3 server.py
```
By default, the server listens on `127.0.0.1:53`. You may need root privileges to bind to port 53.

### Querying the Server
You can test the server using `dig`:

```sh
dig segfault.local @127.0.0.1
```

### Future Improvements
- to add command line arguments
- to add logging mechanism
- to have a startup script for the systemd service
- to have our own `help` and `man` page
- to support other record types
