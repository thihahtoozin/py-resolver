import socket
import re
import glob
import argparse
import querylogger
from zoneparser import *

parser = argparse.ArgumentParser(description="Simple DNS Resolver")
parser.add_argument("addr", help="specify the layer 3 address on listen on")
parser.add_argument("-p", "--port", type=int, help="specify the layer 4 udp port address (default = 53)")
parser.add_argument("--log_level", choices=['debug', 'info', 'warning', 'error', 'critical'], help="Set log level (default = 'info')")
parser.add_argument("--log_file", help="specify the destination log file to be stored (default = 'logs/queries.log')")

args = parser.parse_args()

#zone_file: str = 'zones/segfault.local.zone'
#jzone_file: str = 'jzones/segfault.local.json'

jzone_files = glob.glob('jzones/*.json')
zone_file = glob.glob('zones/*.zone')

if not args.log_file:
    log_file = "logs/queries.log"
else:
    log_file = args.log_file

ip: str = args.addr
port: int = 53
if args.port:
    port: int = args.port

if args.log_level:
    qlogger = querylogger.Logger(log_file, args.log_level)
else:
    qlogger = querylogger.Logger(log_file, "info")


#records: dict = read_zone_file(zone_file[0])
recs_dict = read_zone_file(zone_file[0])
#ttl, origin, soa, recs = load_zone_file(record)
load_zone_file(recs_dict)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((ip,port))
print(f"[+] Listening on {ip}:{port} ")

def get_question_domain(data: bytes) -> tuple:
    domain_lst = []
    i = 0
    while data[i] != 0: # stop while reaching null byte
        length = data[i] # first give the length of next segment
        i += 1 # move to actual segment
        domain_lst.append(data[i:i+length].decode()) # decode the segment
        i += length
    question_type = data[i+1: i+3]
    return(domain_lst, question_type)

def generate_zone_profiles() -> dict:
    zone_profiles: dict = {}
    for jzone in jzone_files:
        with open(jzone, 'r') as zonedata:
            data = json.load(zonedata)
            zone_name = data['$ORIGIN']
            zone_profiles[zone_name] = data
    #pprint(zone_profiles)
    return zone_profiles

zone_profiles = generate_zone_profiles()

def getzone(domain_list: list) -> dict: # Getting the specified zone dictionary from the zone profiles 
    if domain_list[0] in ['www', 'ssh']:
        zone_name: str = '.'.join(domain_list[1:]) + '.'
    else: 
        zone_name: str = '.'.join(domain_list) + '.'
    #print(zone_name)
    if zone_name in zone_profiles:
        return zone_profiles[zone_name]
    else:
        return {}

def get_records(data):
    dm_lst, q_type = get_question_domain(data) #list, bytes
    qt = ''
    if q_type == b"\x00\x01":
        qt = 'A'

    zone: dict = getzone(dm_lst)
    #print('ZONE---------')
    #pprint(zone)

    filtered_recs: dict = {} # zones with requested type(i.e. A)
    for k,v in zone.items():
        if 'A' in v:
            filtered_recs[k] = v

    # filtered_recs => {'ns1': ['A', '192.168.100.254'], 'ssh': ['A', '192.168.100.254'], 'www': ['A', '192.168.100.254']}

    return (filtered_recs, qt, dm_lst)

def get_flags(data: bytes) -> bytes:
    flags_byte1:bytes = bytes(data[0])
    flags_byte2:bytes = bytes(data[1])
    # flags_byte1[0] -> integer representing the byte

    qr: str = '1' # 1 for response
    opcode: str = f"{(flags_byte1[0] >> 3) & 0b1111:04b}" # extracting opcode # 0
    aa: str = '1'       # Authoritative Answer
    tc: str = '0'       # TrunCation
    rd: str = '0'       # Recursion Desired (not going to support recursion)
    ra: str = '0'       # Recursion Available 
    z: str = '000'      # Reserved
    rcode: str = '0000' # Response Code (no error)

    ## RESPONSE
    flags: bytes = qr + opcode + aa + tc + rd + ra + z + rcode
    flags: bytes = int(flags, 2).to_bytes(2, byteorder='big')
    return flags

def extract_question(data: bytes) -> bytes:  # extract dns question from the client's query

    dm_lst, q_type = get_question_domain(data[12:]) # remove header (cut off first 12 bytes)
    raw_data = b''

    for part in dm_lst:
        d_len = len(part)
        raw_data += bytes([d_len])

        for char in part:
            raw_data += ord(char).to_bytes(1, byteorder='big')

    raw_data += b'\x00' # append null byte to terminate the string
    
    q_class: bytes = (1).to_bytes(2, byteorder='big') # \x00\x01 for Class IN

    q = raw_data + q_type + q_class

    return q

def generate_answer(filtered_recs: dict, rec_t: str, sub_dm: str, r_value: list) -> bytes:
    dm_name_b: bytes = b'\xc0\x0c' # 0c means 12 in hexa-decimal meaning the name can be found from the 12-bytes offset from the start of the dns packet(domain name using message compression)

    # Type
    if rec_t == 'A':
        rec_type_b: bytes = b'\x00\x01'
    elif rec_t == 'CN': # for Canonical Name (reversed dns query)
        rec_type_b: bytes = b'\x00\x05'

    # Class
    rec_class_b: bytes = b'\x00\x01' # for IN

    soa_ttl_b: bytes = int('3600').to_bytes(4, byteorder='big') # we have to hard code it for now (we need to fix the code to extract from the zone file)
    ans_len_b: bytes = b'\x00\x04' # length of the ip address 
    grepped_ip_l: list = []

    grepped_ip_l =  r_value[1].split('.') #find in filtered_recs # ['192', '168', '100', '1']

    ans_data_l = []
    for grepped_ip_part in grepped_ip_l: 
        ans_data_l.append(int(grepped_ip_part)) # [192, 168, 100, 1] 

    ans_data_b: bytes = b''
    for ans_data in ans_data_l:
        ans_data_b += ans_data.to_bytes(1, byteorder='big')

    ans_b: bytes = dm_name_b + rec_type_b + rec_class_b + soa_ttl_b + ans_len_b + ans_data_b

    return ans_b

def get_query_info(data):
    pass

def build_rep(data: bytes) -> bytes:
    
    # HEADER
    trans_id: bytes = data[:2]           # TransactionID
    flags: bytes = get_flags(data[2:4])  # Flags
    qd_count: bytes = b'\x00\x01'        # Question Count 
    an_count: bytes = len(get_records(data[12:])[0]).to_bytes(2, byteorder='big') # Answer Count
    ns_count: bytes = (0).to_bytes(2, byteorder='big') # Nameserver Count 
    ar_count: bytes = (0).to_bytes(2, byteorder='big') # Additional Count

    dns_header: bytes = trans_id+flags+qd_count+an_count+ns_count+ar_count

    dns_body: bytes = b''
    
    grepped_records, rectype, dm_name_l = get_records(data[12:])
    #dm_name = '.'.join(dm_name_l) # segfault.local

    dns_question: bytes = extract_question(data)
    
    #client_query_l, client_query_type = get_question_domain(data[12:]) 

    dns_answer: bytes = b''
    for sub_d, r_value in grepped_records.items():
        answers: bytes = generate_answer(grepped_records, rectype, sub_d, r_value)
        dns_answer += answers

    # RESPONSE
    rep: bytes = dns_header + dns_question + dns_answer

    return rep

def main() -> None:
    while 1:
        data, addr = s.recvfrom(512) # receive 512 bytes of dns request
        #print(type(data)) <class 'bytes'>
        src_addr, src_port = addr
        query_string, query_type = get_question_domain(data[12:])
        query_string = '.'.join(query_string)
        if query_type == b'\x00\x01':
            query_type = 'A' 
        
        msg = f"{src_addr}:{src_port} queries {query_string} of type {query_type}"
        qlogger.add_log_info(msg)
        
        rep: bytes = build_rep(data)
        #print(recs)
        s.sendto(rep, addr)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print("KeyboardInterrupt detected...")
        print("Quitting...")

