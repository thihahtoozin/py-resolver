import re
import glob
import json
from pprint import pprint

def read_zone_file(zone_file: str) -> dict: # takes zone file as input
    
    records: dict = {}
    clean_lines: list = []
    with open(zone_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = re.sub(r";.*", "", line).strip()  # Remove comments
            if line: # Ignore empty lines
                clean_lines.append(line)
        # Reconstruct SOA Records
        parsed_records = []
        soa_record = []
        inside_soa = False

        for line in clean_lines:
            parts: list = line.split()
            for i in range(len(parts)):
                parts[i]: str = parts[i].replace('(', '')

            if 'SOA' in parts:
                inside_soa: bool = True
                soa_record: list = parts[:3] # ['@', 'NS', 'SOA']
                soa_data: list = parts[3:]   # The rest of the SOA record

            elif inside_soa:
                soa_data.extend(parts)
                if ')' in parts: # End of SOA block
                    inside_soa = False
                    soa_data.remove(')')   # Remove closing bracket from the list
                    parsed_records.append(soa_record + [' '.join(soa_data)]) # Join SOA Fields
            else:
                parsed_records.append(parts)

        #print(parsed_records)
        for rcs in parsed_records:
            name: str = rcs[0]
            if '@' in rcs:
                name: str = name + '_' + rcs[2]

            if len(rcs) > 2: # we have a problem here (the previous '@''s values are overwritten)
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


    
