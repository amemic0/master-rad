import re
import yaml
from collections import defaultdict

ALL_LABELS = [
    "baza-podataka",
    "intersection3-app",
    "intersection4-app",
    "server-app",
    "server2-app",
    "server3-app",
    "server5-app"
]

def parse_firewall_file(file_path):
    blocked = defaultdict(list)
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("<") and line.endswith(">"):
                # Regex: <SRC DEST PROTO START-END>
                m = re.match(r"<\s*(\S+)\s+(\S+)\s+(\S+)\s+(\d+)-(\d+)\s*>", line)
                if m:
                    src_pod, dest_pod, proto, start, end = m.groups()
                    start_port = int(start)
                    end_port = int(end)
                    blocked[(src_pod, dest_pod, proto.upper())].append((start_port, end_port))
    return blocked

def invert_port_ranges(blocked_ranges):
    """
    Pomoćna funkcija koja iz liste blokiranih portova (npr. [(0, 8079), (8081, 65535)])
    vraća listu 'dozvoljenih' portova (npr. [(8080, 8080)]).
    Sve je unutar 1..65535 (0 ionako nije validan port).
    """
    blocked_ranges = sorted(blocked_ranges, key=lambda r: r[0])
    allowed = []
    CURRENT_MIN = 1

    for (start, end) in blocked_ranges:
     
        if end < 1:
            continue
        start = max(1, start)
        if start > CURRENT_MIN:
            allowed.append((CURRENT_MIN, start - 1))
        CURRENT_MIN = max(CURRENT_MIN, end + 1)

    # Ako nakon svega ima rupa do 65535
    if CURRENT_MIN <= 65535:
        allowed.append((CURRENT_MIN, 65535))

    return allowed

def generate_network_policies(blocked, namespace="master-rad"):
    """
    Generiše listu NetworkPolicy objekata, po 1 za svaki 'dest_pod' iz ALL_LABELS.
    Uz to, DODAJE dodatno pravilo koje dozvoljava sav (TCP) promet
    iz namespace-a `cattle-monitoring-system` (gdje su Prometheus/Grafana),
    kako bi se monitoring alati uvijek mogli spojiti.

    Policy:
      - U 'ingress' stavimo pravila 'from' = svaki mogući src_pod
      - Ports = 'invert' blokiranih range-ova (tj. dozvoljeni range)
      - Ako je sve blokirano, nećemo generisati 'from' za taj src, jer nema dozvoljenih portova
      - Ako (src,dest) nije uopšte u blocked => dozvoljeno je sve (1..65535)
    """
    policies = []

    for dest_pod in ALL_LABELS:
        netpol = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"auto-deny-{dest_pod}",
                "namespace": namespace
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {"app": dest_pod}
                },
                "policyTypes": ["Ingress"],
                "ingress": []
            }
        }

     
        for src_pod in ALL_LABELS:
            if src_pod == dest_pod:
                continue

            # Napravimo dictionary: protocol => list of (start, end)
            blocked_for_src = {}
            for (s, d, proto) in blocked.keys():
                if s == src_pod and d == dest_pod:
                    blocked_for_src.setdefault(proto, []).extend(blocked[(s, d, proto)])

            # Ako nema unosa => Dozvoljeno sve
            if not blocked_for_src:
                netpol["spec"]["ingress"].append({
                    "from": [
                        {"podSelector": {"matchLabels": {"app": src_pod}}}
                    ],
                    "ports": [
                        {
                            "protocol": "TCP",
                            "port": 1,
                            "endPort": 65535
                        }
                    ]
                })
            else:
                for proto, blocked_ranges in blocked_for_src.items():
                    allowed_ranges = invert_port_ranges(blocked_ranges)
                    if not allowed_ranges:
                        continue  # sve blokirano -> ne dodaj from
                    ports_list = []
                    for (start_p, end_p) in allowed_ranges:
                        if start_p == end_p:
                            ports_list.append({
                                "protocol": proto,
                                "port": start_p
                            })
                        else:
                            ports_list.append({
                                "protocol": proto,
                                "port": start_p,
                                "endPort": end_p
                            })
                    netpol["spec"]["ingress"].append({
                        "from": [
                            {"podSelector": {"matchLabels": {"app": src_pod}}}
                        ],
                        "ports": ports_list
                    })

        netpol["spec"]["ingress"].append({
            "from": [
                {
                    "namespaceSelector": {
                        "matchLabels": {
                            "kubernetes.io/metadata.name": "cattle-monitoring-system"
                        }
                    }
                }
            ],
            "ports": [
                {
                    "protocol": "TCP",
                    "port": 1,
                    "endPort": 65535
                }
            ]
        })
        # ------------------------------------------------

        policies.append(netpol)

    return policies


def save_yaml(data, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump_all(data, f, default_flow_style=False)

def main():
    input_file = "FirewallSetup_Cleaned.txt" 
    output_file = "network_policy.yaml"

    blocked_dict = parse_firewall_file(input_file)
    netpols = generate_network_policies(blocked_dict, namespace="master-rad")

    save_yaml(netpols, output_file)

    print(f"Generisano je {len(netpols)} NetworkPolicy objekata i sačuvano u {output_file}")

if __name__ == "__main__":
    main()
