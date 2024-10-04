#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import argparse
import textwrap

# Simple vulnerability scanner based on OWASP Top 10 2021

# Improved minimal ASCII art for OWASP Checker
ASCII_ART = """
         _.-=-._ 
       o~`  '  `~o
       \\    OWASP  /
        `..____..-' 
   Designed by Ali Baykara
"""

# Risk ratings
RISK_RATINGS = {
    "A01:2021 - Broken Access Control": "high",
    "A02:2021 - Cryptographic Failures": "high",
    "A03:2021 - Injection": "high",
    "A04:2021 - Insecure Design": "medium",
    "A05:2021 - Security Misconfiguration": "medium",
    "A06:2021 - Vulnerable and Outdated Components": "medium",
    "A07:2021 - Identification and Authentication Failures": "high",
    "A08:2021 - Software and Data Integrity Failures": "high",
    "A09:2021 - Security Logging and Monitoring Failures": "low",
    "A10:2021 - Server-Side Request Forgery (SSRF)": "high"
}

# Class to test the target URL for vulnerabilities
class OWASPTester:
    def __init__(self, target_url):
        self.target_url = target_url

    def check_broken_access_control(self):
        try:
            response = requests.get(f"{self.target_url}/admin", timeout=10)
            if response.status_code == 200:
                return "A01:2021 - Broken Access Control"
        except requests.exceptions.RequestException:
            pass
        return None

    def check_injection(self):
        try:
            payload = {"username": "admin' OR '1'='1", "password": "password"}
            response = requests.post(f"{self.target_url}/login", data=payload, timeout=10)
            if "Welcome" in response.text or response.status_code == 200:
                return "A03:2021 - Injection"
        except requests.exceptions.RequestException:
            pass
        return None

    def check_security_misconfiguration(self):
        try:
            response = requests.get(f"{self.target_url}/phpinfo.php", timeout=10)
            if response.status_code == 200:
                return "A05:2021 - Security Misconfiguration"
        except requests.exceptions.RequestException:
            pass
        return None

    def check_outdated_components(self):
        try:
            response = requests.get(self.target_url, timeout=10)
            if "Server: Apache/2.2" in response.headers.get("Server", ""):
                return "A06:2021 - Vulnerable and Outdated Components"
        except requests.exceptions.RequestException:
            pass
        return None

    def check_ssrf(self):
        try:
            response = requests.post(f"{self.target_url}/ssrf-test", data={"url": "http://localhost:8080"}, timeout=10)
            if "local resource" in response.text.lower():
                return "A10:2021 - Server-Side Request Forgery (SSRF)"
        except requests.exceptions.RequestException:
            pass
        return None

    def run_tests(self):
        # Running vulnerability tests
        vulnerabilities = []

        broken_access_control = self.check_broken_access_control()
        if broken_access_control:
            vulnerabilities.append(broken_access_control)

        injection = self.check_injection()
        if injection:
            vulnerabilities.append(injection)

        security_misconfiguration = self.check_security_misconfiguration()
        if security_misconfiguration:
            vulnerabilities.append(security_misconfiguration)

        outdated_components = self.check_outdated_components()
        if outdated_components:
            vulnerabilities.append(outdated_components)

        ssrf = self.check_ssrf()
        if ssrf:
            vulnerabilities.append(ssrf)

        return vulnerabilities

    def get_risk_rating(self, vulnerability):
        # Getting the risk rating of the vulnerability
        return RISK_RATINGS.get(vulnerability, "unknown")

# Main function to parse arguments and run the tests
def main():
    parser = argparse.ArgumentParser(description="OWASP Checker - A simple OWASP Top 10 vulnerability scanner")
    parser.add_argument("-t", "--target", required=True, help="Target URL to test")
    parser.add_argument("-o", "--output", required=True, help="Output file to save the results")

    args = parser.parse_args()

    # Validate and format the target URL
    target = args.target
    if not target.startswith(("http://", "https://")):
        target = "http://" + target

    # Run OWASP tests
    tester = OWASPTester(target)
    found_vulnerabilities = tester.run_tests()

    # Prepare the output
    output = textwrap.dedent(f"""{ASCII_ART}

Target: {target}
Results:
""")

    if found_vulnerabilities:
        for vuln in found_vulnerabilities:
            risk = tester.get_risk_rating(vuln)
            output += f"  - Vulnerability Found: {vuln} - Risk Level: {risk}\n"
    else:
        output += "  No vulnerabilities found.\n"

    # Write the output to a file
    with open(args.output, "w") as file:
        file.write(output)

    # Print the ASCII art and results to the terminal
    print(output)

    # Print completion message
    print(f"Scan completed. Results saved to {args.output}")

if __name__ == "__main__":
    main()
