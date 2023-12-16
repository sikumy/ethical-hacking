import json
import re
import sys
import argparse
import ipaddress

def is_private_ip(ip):
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        # Handle invalid IP addresses
        return False

def parse_massdns_output(file_path):
    public_a_records = {}
    private_a_records = {}
    cname_records = {}

    with open(file_path, 'r') as file:
        for line in file:
            line = line.rstrip('.\n')
            match = re.match(r'(.*)\s+(A|CNAME)\s+(.*)', line)
            if match:
                domain, record_type, value = match.groups()
                domain = domain.rstrip('.')

                if record_type == 'A':
                    if is_private_ip(value):
                        private_a_records.setdefault(value, []).append(domain)
                    else:
                        public_a_records.setdefault(value, []).append(domain)
                elif record_type == 'CNAME':
                    cname_records[domain] = value

    output_json = {
        "Public A Records": public_a_records,
        "Private A Records": private_a_records,
        "CNAME Records": cname_records
    }

    return json.dumps(output_json, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Parse massdns output and convert it to JSON.")
    parser.add_argument("input_file", help="The massdns output file.")
    parser.add_argument("-o", "--output", help="Output file to save the results.")
    args = parser.parse_args()

    json_output = parse_massdns_output(args.input_file)
    print(json_output)

    if args.output:
        with open(args.output, 'w') as output_file:
            output_file.write(json_output)

if __name__ == "__main__":
    main()