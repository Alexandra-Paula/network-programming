import dns.resolver
import dns.reversename 
import ipaddress
import json
import sys

CONFIG_FILE = "config.json"

def save_dns(ip):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"dns": ip}, f)

def load_dns():
    try: 
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)["dns"]
    except FileNotFoundError:
        return None

def is_ip(ipval):
    try:
        ipaddress.ip_address(ipval)
        return True
    except ValueError:
        return False

if len(sys.argv) > 3:
    print("Usage:\ndns-resolver resolve <domain>\ndns-resolver resolve <ip>\ndns-resolver dns <ip>")
    exit(1)

#load a user set dns, if not use the default
resolver = dns.resolver.Resolver()
saved_dns = load_dns()
if saved_dns:
    resolver.nameservers = [saved_dns]

command = sys.argv[1]
argument = sys.argv[2]

if command == "resolve":
    if is_ip(argument):
        #valid id address passed, return domain to user
        try: 
            rev_name = dns.reversename.from_address(argument)
            result = resolver.resolve(rev_name, 'PTR') 
            for val in result:
                print('Domain Name: ', val.to_text())
        except dns.resolver.NXDOMAIN:
            print("No domain found for this IP :(")
    else:
        #an invalid ip address was passed (assume it is a domain), try to return ip address to user 
        try:
            result = resolver.resolve(argument, 'A')
            for ipval in result:
                print('IP', ipval.to_text())
        except dns.resolver.NXDOMAIN: 
            print("Invalid domain name or ip address")
        except dns.resolver.LifetimeTimeout:
            print("Invalid DNS Server")

elif command == "use-dns":
    if not is_ip(argument):
        print("Invalid IP")
        exit(1)
    save_dns(argument)
    print(f"DNS server changed to {argument}")
        


