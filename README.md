# PyResolver – Python-based DNS resolver

**PyResolver** is the minimalist DNS implementation for the local network written in python. A simple, lightweight DNS server written in Python that can simply resolve domain names and support custom mappings. This project is designed for educational purposes, local network DNS resolution, or as a customizable alternative to public DNS resolvers.

## Description

This project is a python-based DNS resolver running on the udp protocol that can resolve domain names and return appropriate IP addresses based on predefined records.
By default, it listens on udp port 53 on the specified ip address and responds to DNS queries with the answers defined on zone files.

It is useful for:  
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
### Help Menu

```
python3 main.py -h
```

### Basic Usage
You may need root privileges to bind to port 53.
```
sudo python3 main.py 127.0.0.1
```
Replace `127.0.0.1` with the ip address of the interface being used if you are not listening on the loopback interface.

By default, the server listens on the udp port 53 (i.e. `127.0.0.1:53`). But you can specify this to the desired port address using `-p` or `--port`

```
sudo python3 main.py 127.0.0.1 -p 1338
```

### Querying the Server Using `dig`
You can test the server using `dig`:

```sh
dig segfault.local @127.0.0.1
```

### Logging

By default, logs are added to the `logs/queries.log` file.
```
cd py-resolver
tail -f logs/queries.log
```

However, you can specify the destination log file by setting `--log_file` optional argumennt. 

```
sudo python3 main.py --log_file /path/to/file.log 127.0.0.1
```

You can also specify the log level using `--log_level`. This can be one of debug, info, warning, error or critical.
```
sudo python3 main.py --log_file /path/to/file.log --log_level debug 127.0.0.1
```
By default `log_level` is set to "info".

### Future Improvements
- to have a startup script for the systemd service
- to have its own `manual` page
- to support other record types


### Referennces
- [RFC 1035 Specification](https://www.ietf.org/rfc/rfc1035.txt)
- [howCode - Make Your Ownn DNS Server](https://www.youtube.com/watch?v=HdrPWGZ3NRo&list=PLBOh8f9FoHHhvO5e5HF_6mYvtZegobYX2)
