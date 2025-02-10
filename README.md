***Sigurnosna orkestracija u Kubernetesu***

U narednih nekoliko rečenica, izvršen je prikaz osnovnih komponenti praktičnog dijela rada Sigurnosna orkestracija u kubernetesu. 

Server1 predstavlja http server koji parsira tijelo dolaznih http zahtjeva i upisuje podatke u bazu podataka.

Server2 predstavlja http server koji parsira tijelo dolaznih http zahtjeva i upisuje podatke u bazu podataka.

Server3 vrši parsiranje dolaznih zahtjeva i u zavisnosti od polja u http zahtjevu vrši pristupanje bazi i upis u istu, ili vrši usmjeravanje zahtjeva prema serveru1 i serveru2. 

Server4 predstavlja http server koji parsira tijelo dolaznih http zahtjeva i upisuje podatke u bazu podataka. Deployment za isti se nalazi u sklopu foldera server2.

Traffic_generator1 predstavlja aplikaciju koja na svakih 1s upućuje http zahtjev prema serveru 4. 

Traffic_generator2 predstavlja aplikaciju koja na svakih 1s upućuje http zahtjev prema serveru 3 (forwarder). 

**VEREFOO**

File *service_graph1.xml* predstavlja ulaznu xml datoteku koja se prilikom pokretanja simulacije dostavlja do VEREFOO servera.
File *result.xml* predstavlja rezultat VEREFOO simulacije. Navedeni file je sličan ulaznom xml file i razlikuje se isključivo po tome što sadrži alocirane firewall elemente.

**parser3** predstavlja python skriptu koja će na osnovu bilo koje promjene u datoteci **result.xml** izvršiti parsiranje iste i u datoteku **FirewallSetup.txt** smjestiti nova firewall pravila.

**mappingJob.py** predstavlja python skriptu koja će iz file-a **FirewallSetup.txt** izvući pravila za firewall i izmapirati ista za odgovorajuće pod-ove, s obzirom na to da se network policy primjenjuje na nivou pod-ova.

**generisi_yaml.py** predstavlja python skriptu koja uzima ulazni file **FirewallSetup_Cleaned.txt** i generiše yaml datoteku **network_policy.yaml** koja u sebi sadrži network policy za Kubernetes klaster.

**apply_network_policy.py** predstavlja python skriptu koja učitava datoteku **network_policy.yaml** i putem Kubernetes API poziva primjenjuje network policy na Kubernetes klaster.

