# PyResolver – Python-based DNS resolver

**PyResolver** is a lightweight, Python-based DNS server designed for local network resolution and custom domain mapping. It supports local zone files. This project is designed for educational purposes, local network DNS resolution, or as a customizable alternative to public DNS resolvers.

## Description

**PyResolver** is a Python-based DNS resolver that operates over UDP, resolving domain names and returning IP addresses based on predefined records.
By default, it listens on UDP port 53 on the specified ip address and responds to DNS queries with the answers defined on zone files.
```
+-----------+-----(queries)-->+-----------+                     +------------------+
| DNS Client|                 | PyResolver| -----(forward)----> | External Resolver|
+-----------+<---(response)---+-----------+                     +------------------+
     ^                              |                                    |
     |                              |                                    v
     |<------------(relay)----------|<-----------(response)--------------+
```
If the client queries the records that are not defined in the local zone files, **PyResolver** forwards the client's request towards the external DNS resolver(a.k.a. recursive resolver) `8.8.8.8` if `-r` flag is set. However, **PyResolver** does not cache external DNS records.

**PyResolver** is useful for:  
- Setting up a local DNS server for development or testing  
- Overriding domain resolutions for specific domains  
- Learning how DNS servers work  

## Features  

✔️ Supports **A** and **CNAME** record types

✔️ Can forward **DNS queries** to external recursive resolvers such as `8.8.8.8`, `1.1.1.1`

✔️ **Custom domain mappings** using zone files

✔️ Can run on **any port**, not just on 53 (useful for testing)  

✔️ **Minimal dependencies** (uses Python’s built-in socket module)  

## Installation
Just install `python3` and clone this repository:
```
git clone https://github.com/thihahtoozin/py-resolver
```

### Requirements
- Requires Python 3.13.2 or later


## Configuration
You can have custom configurations by adding or modifying zone files under `zones/` directory
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
Zone files should be placed under `zones/` directory for **PyResolver** to recognize them.

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
Replace `127.0.0.1` with the IP address of the interface being used if you are not listening on the loopback interface.

By default, the server listens on the UDP port 53 (i.e. `127.0.0.1:53`). But you can specify this to the desired port address using `-p` or `--port`

```
sudo python3 main.py 127.0.0.1 -p 1338
```

### Querying the Server Using `dig`
You can test the server using `dig`:

```sh
dig segfault.local @127.0.0.1
```

### Enabling the DNS Forwarding
You can make recursive dns queries by enabling `-r` flag
```
sudo python3 main.py -r 127.0.0.1
```
**PyResolver** does this by forwarding DNS queries from the client (such as `dig`) towards the external recursive DNS resolver so that the **PyResolver** can relay the response back the client. By default, external DNS queries are forwarded to `8.8.8.8`. You can set the external recursive resolver with the `-e` flag.
```
sudo python3 main.py -r -e 1.1.1.1:53 127.0.0.1
```
`-e` has no effect unless `-r` is enabled, as external resolution is only performed when forwarding is enabled.

### Logging

By default, logs are stored the `logs/queries.log` file.
```
cd py-resolver
tail -f logs/queries.log
```

You can specify a custom log file using the `--log_file` option.

```
sudo python3 main.py --log_file /path/to/file.log 127.0.0.1
```

You can also specify the log level using `--log_level`. This **can be** one of: debug, info, warning, error or critical.
```
sudo python3 main.py --log_file /path/to/file.log --log_level debug 127.0.0.1
```
By default `log_level` is set to "info".

### Future Improvements
- to have a startup script for the systemd service
- to have its own `manual` page
- to support other record types


### References
- [RFC 1035 Specification](https://www.ietf.org/rfc/rfc1035.txt)
- [howCode - Make Your Own DNS Server](https://www.youtube.com/watch?v=HdrPWGZ3NRo&list=PLBOh8f9FoHHhvO5e5HF_6mYvtZegobYX2)
