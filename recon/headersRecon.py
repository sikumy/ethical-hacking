#!/usr/bin/python3

import json
import argparse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm

class CustomRequestError(Exception):
    def __init__(self, message):
        super().__init__(message)

def get_headers(url):
    try:
        # Disable SSL warnings
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        response = requests.get(url, verify=False)
        response.raise_for_status()
        headers = dict(response.headers)
        return headers
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            raise CustomRequestError(f"Error: 404 Not Found for URL: {url}")
        else:
            raise CustomRequestError(f"HTTP Error: {e}")
    except requests.exceptions.SSLError as e:
        raise CustomRequestError(f"SSL Error: {e}")
    except requests.exceptions.RequestException as e:
        raise CustomRequestError(f"Request Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Fetch and display HTTP response headers for a list of domains without verifying SSL.")
    parser.add_argument("-l", "--list", required=True, help="List of domains to query")
    parser.add_argument("-o", "--output", help="Output file for the JSON result")
    args = parser.parse_args()

    with open(args.list, "r") as file:
        domains = [line.strip() for line in file.readlines()]

    result = {}
    for domain in tqdm(domains, desc="Processing", unit="domain"):
        try:
            headers = get_headers(domain)
            result[domain] = headers
        except CustomRequestError as e:
            print(e)

    output_json = json.dumps(result, indent=4)
    print(output_json)

    if args.output:
        with open(args.output, "w") as output_file:
            output_file.write(output_json)

if __name__ == "__main__":
    main()
