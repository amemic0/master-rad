def load_ip_mapping(mapping_file):
    mapping = {}
    with open(mapping_file, 'r') as file:
        for line in file:
            parts = line.strip('<>\n').split(' - ')
            if len(parts) == 2:
                ip, pod = parts
                mapping[ip.strip()] = pod.strip()
    return mapping


def replace_ips(line, ip_mapping):
    """
    Zamjenjuje IP adrese odgovarajućim nazivima iz mape.
    """
    parts = line.strip('<>\n').split()
    if len(parts) > 2:
        # Posebna logika za 192.168.172.177
        if parts[1] == "192.168.172.177":
            if len(parts) > 2 and parts[2] == "192.168.172.178":
                parts[1] = "intersection3-app"
            else:
                parts[1] = "intersection4-app"

        # Mapiranje ostalih IP adresa
        mapped_parts = [ip_mapping.get(p, p) if p not in ("intersection3-app", "intersection4-app") else p for p in parts[1:]]
        return "<" + " ".join(mapped_parts) + ">\n"
    return line


def clean_firewall_rules(input_file, mapping_file, output_file, pods_file):
   
    ip_mapping = load_ip_mapping(mapping_file)

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            if line.startswith("Firewall"):
                outfile.write(line)
                continue
            cleaned_line = replace_ips(line, ip_mapping)
            outfile.write(cleaned_line)

    # Sada ponovo otvaramo output_file u append ('a') modu da dodamo pods.txt
    with open(output_file, 'a') as outfile, open(pods_file, 'r') as pods:
        outfile.write("\nOvo je spisak svih matchlabes:\n\n")
        outfile.write(pods.read())


# Nazivi datoteka
input_filename = "FirewallSetup.txt"
mapping_filename = "mapping.txt"
output_filename = "FirewallSetup_Cleaned.txt"
pods_filename = "pods.txt"

# Pokretanje funkcije
clean_firewall_rules(input_filename, mapping_filename, output_filename, pods_filename)
print(f"Proces završen! Očišćeni i mapirani podaci su sačuvani u {output_filename}")
