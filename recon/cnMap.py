import dns.resolver
import argparse
import json
import csv

def resolve_cname_recursive(domain, depth=5, resolvers=None):
    if depth == 0:
        return []

    try:
        resolver = dns.resolver.Resolver()
        if resolvers:
            resolver.nameservers = resolvers

        answers = resolver.resolve(domain, 'CNAME')
        cname_results = [str(r.target) for r in answers]
        recursive_results = []

        for cname in cname_results:
            recursive_results.extend(resolve_cname_recursive(cname, depth - 1, resolvers))

        return cname_results + recursive_results

    except dns.resolver.NoAnswer:
        return []
    except dns.resolver.NXDOMAIN:
        return []
    except dns.exception.Timeout:
        return []

def resolve_cnames_from_file(file_path, depth=5, resolvers=None):
    with open(file_path, 'r') as file:
        domains = [line.strip() for line in file.readlines()]

    results = {}
    for domain in domains:
        cname_results = resolve_cname_recursive(domain, depth, resolvers)
        if cname_results:
            results[domain] = cname_results

    return results

def export_to_file(results, output_file):
    with open(output_file, 'w') as file:
        json.dump(results, file, indent=4)

def export_to_csv(results, csv_file):
    with open(csv_file, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        for domain, cnames in results.items():
            for cname in cnames:
                csv_writer.writerow([domain, cname])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resolve CNAME records recursively from a list of domains.")
    parser.add_argument("-l", "--list", dest="file_path", required=False, help="Path to the file containing domains")
    parser.add_argument("-o", "--output", help="Path to the output file (optional)")
    parser.add_argument("--csv", help="Path to the CSV output file (optional)")
    parser.add_argument("--resolvers", help="Path to the file containing DNS resolvers (optional)")
    parser.add_argument("-d", "--depth", type=int, default=5, help="Depth of recursive resolution (default: 5)")

    args = parser.parse_args()

    # Verifica si no se han proporcionado argumentos requeridos
    if not args.file_path:
        parser.print_help()
        exit(1)

    resolvers = None
    if args.resolvers:
        with open(args.resolvers, 'r') as resolvers_file:
            resolvers = [line.strip() for line in resolvers_file.readlines()]

    results = resolve_cnames_from_file(args.file_path, depth=args.depth, resolvers=resolvers)

    # Imprime los resultados en formato JSON
    print(json.dumps(results, indent=4))

    if args.output:
        export_to_file(results, args.output)

    if args.csv:
        export_to_csv(results, args.csv)
