package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"strings"
)

type Certificate struct {
	CommonName string `json:"common_name"`
	NameValue  string `json:"name_value"`
}

func main() {
	// Define command-line arguments
	domainArg := flag.String("d", "", "Domain name")
	orgArg := flag.String("org", "", "Organization name")
	outputFile := flag.String("o", "", "Output file to save the results (optional)")
	flag.Parse()

	// Show help if neither a domain nor an organization name is provided
	if *domainArg == "" && *orgArg == "" {
		fmt.Println("Usage:")
		flag.PrintDefaults()
		return
	}

	// Ensure that only one type of query is specified
	if *domainArg != "" && *orgArg != "" {
		log.Fatal("Please specify only one type of query: either a domain with -d or an organization with -org")
	}

	query := *domainArg
	if *orgArg != "" {
		query = *orgArg
	}

	// Perform the HTTP request
	resp, err := http.Get("https://crt.sh/?" + "q=" + strings.ReplaceAll(query, " ", "+") + "&output=json")
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()

	// Read and parse the JSON response body
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatal(err)
	}

	var certificates []Certificate
	err = json.Unmarshal(body, &certificates)
	if err != nil {
		log.Fatal("Error parsing JSON:", err)
	}

	// Remove duplicates and prepare the output
	domainSet := make(map[string]struct{})
	var output string
	for _, cert := range certificates {
		// For domain queries, add only NameValue
		if *domainArg != "" {
			for _, name := range strings.Split(cert.NameValue, "\n") {
				addDomainsToSet(&domainSet, name)
			}
		} else {
			// For organization queries, add only CommonName
			addDomainsToSet(&domainSet, cert.CommonName)
		}
	}

	for domain := range domainSet {
		output += domain + "\n"
	}

	// Print the output to console
	fmt.Print(output)

	// Write the results to a file if specified
	if *outputFile != "" {
		err := ioutil.WriteFile(*outputFile, []byte(output), 0644)
		if err != nil {
			log.Fatal("Error writing to file:", err)
		}
	}
}

func addDomainsToSet(set *map[string]struct{}, domain string) {
	domain = strings.ToLower(strings.TrimSpace(domain))
	if domain != "" && !strings.ContainsAny(domain, " &") && strings.Contains(domain, ".") {
		(*set)[domain] = struct{}{}
	}
}
