import re
import glob
import json
from pprint import pprint

def read_zone_file(zone_file: str) -> dict: # takes a zone file as input
    
    records: dict = {}
    clean_lines: list = [] # list of each line without comments and white spaces 
    with open(zone_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = re.sub(r";.*", "", line).strip()  # Remove comments
            if line: # Ignore empty lines
                clean_lines.append(line)
        # Reconstruct SOA Records
        parsed_records = [] # list of lists(parts)
        soa_record = [] # ['@', 'IN', 'SOA']
        inside_soa = False

        for line in clean_lines:
            parts: list = line.split()
            # Remove '(' chars in each word
            for i in range(len(parts)):
                parts[i]: str = parts[i].replace('(', '')

            if 'SOA' in parts:
                inside_soa: bool = True
                soa_record: list = parts[:3] # ['@', 'IN', 'SOA']
                soa_data: list = parts[3:]   # [recordns1.segfault.local.,hostmaster.segfault.local.]
            elif inside_soa:
                soa_data.extend(parts)
                if ')' in parts: # End of SOA block
                    inside_soa = False
                    soa_data.remove(')')   # Remove closing bracket from the list
                    parsed_records.append(soa_record + [' '.join(soa_data)]) # Join SOA Fields
            else:
                parsed_records.append(parts)

        #print(parsed_records)
        #[['$TTL', '86400'], ['$ORIGIN', 'segfault.local.'], ['@', 'IN', 'SOA', 'ns1.segfault.local. hostmaster.segfault.local.  2024111401 3600 1800 1209600 86400'], ['@', 'IN', 'NS', 'ns1.segfault.local.'], ['ns1', 'IN', 'A', '172.20.10.14'], ['ssh', 'IN', 'A', '172.20.10.14'], ['www', 'IN', 'A', '172.20.10.14']]
        for rcs in parsed_records:
            name: str = rcs[0]
            if '@' in rcs:
                name: str = name + '_' + rcs[2] # @_SOA

            if len(rcs) > 2:
                records[name] = rcs[2:]
            else:
                records[name] = rcs[1]

        #print(records)
        #{'$TTL': '86400', '$ORIGIN': 'segfault.local.', 
        #'@_SOA': ['SOA', 'ns1.segfault.local. hostmaster.segfault.local.  
            #2024111401 3600 1800 1209600 86400'],
        #'@_NS': ['NS', 'ns1.segfault.local.'], 
        #'ns1': ['A', '192.168.100.254'], 
        #'ssh': ['A', '192.168.100.254'], 
        #'www': ['A', '192.168.100.254']}

    return records

# dump into json file and return tuple of variables
def load_zone_file(records: dict) -> tuple: # load zone data as a json file
    loads: tuple = ()
    ttl: str = ''
    origin: str = ''
    soa: str = ''
    recs: dict = {}

    jzone_file_name = f'jzones/{records['$ORIGIN']}json' # segfault.local.json

    with open(jzone_file_name, 'w') as f:
        json.dump(records, f, indent=2)

    with open(jzone_file_name, 'r') as f:
        data = json.load(f)
        #print(data)
        #print("-" * 10)
        ttl: str = data['$TTL']
        origin: str = data['$ORIGIN']
        soa: str = data['@_SOA']
        recs: dict = {k: v for k, v in data.items() if k not in ["$ORIGIN", "$TTL", "@"]}

        loads = (ttl, origin, soa, recs)

    return loads

if __name__ == '__main__':

    records = []

    zone_files = glob.glob('zones/*.zone')
    for zone_file in zone_files:
        r = read_zone_file(zone_file)
        records.append(r)

    for r in records:
        ttl, origin, soa, recs = load_zone_file(r)

        print(f"TTL : {ttl}")
        print(f"Origin: {origin}")
        print(f"SOA: {soa}")
        print(f"recs: {recs}")
    pprint(records)


    
