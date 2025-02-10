#!/usr/bin/env python3

import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import xml.etree.ElementTree as ET

WATCHED_FILE = "/home/dwh/Desktop/MasterRad/network/result.xml"
XML_FILE_PATH = "/home/dwh/Desktop/MasterRad/network/result.xml"
OUTPUT_FILE_PATH = "/home/dwh/Desktop/MasterRad/network/FirewallSetup.txt"


def extract_blocked_and_group(xml_input_path: str, txt_output_path: str):

    try:
        tree = ET.parse(xml_input_path)
        root = tree.getroot()

        # (A) Prikupiti listu izolacionih pravila (ISOLATION_PROPERTY)
        isolation_rules = []
        prop_elems = root.findall(".//property/property")
        for p in prop_elems:
            prop_name = p.findtext("name", "").strip().upper()
            if "ISOLATION_PROPERTY" in prop_name:
                src = p.findtext("src", "").strip()
                dst = p.findtext("dst", "").strip()
                proto = p.findtext("lv4Proto", "").strip() or "ANY"
                dst_port = p.findtext("dstPort", "").strip() or "*"
                isolation_rules.append((src, dst, proto, dst_port))


        firewall_nodes = root.findall(".//node[functionalType='FIREWALL']")
        firewalls_info = []  

        for fw_node in firewall_nodes:
            fw_name = fw_node.findtext("name") or "UNKNOWN_FIREWALL"
            fw_config = fw_node.find(".//firewall")

            if fw_config is None:
                firewalls_info.append((fw_name, []))
                continue

          
            default_action = fw_config.findtext("defaultAction", "ALLOW").strip().upper()

            deny_rules = []
            rule_elements = fw_config.findall("./elements/elements")
            for rule_el in rule_elements:
                raw_action = rule_el.findtext("action", "").strip().upper()
                source = rule_el.findtext("source", "").strip()
                destination = rule_el.findtext("destination", "").strip()
                protocol = rule_el.findtext("protocol", "").strip() or "ANY"
                dport = rule_el.findtext("dstPort", "").strip() or "*"

                if raw_action == "DENY":
                    deny_rules.append((source, destination, protocol, dport))

            blocked_list = []
            for (srcP, dstP, protoP, portP) in isolation_rules:
                is_deny = False

                for (sA, dA, prA, poA) in deny_rules:
                    if sA == srcP and dA == dstP:
                        match_proto = (prA == "ANY" or protoP == "ANY" or prA == protoP)
                        match_port = (poA == "*" or portP == "*" or poA == portP)
                        if match_proto and match_port:
                            is_deny = True
                            break

                if default_action == "DENY" and not is_deny:
                    is_deny = True

                if is_deny:
                    blocked_list.append((fw_name, srcP, dstP, protoP, portP))
            if blocked_list:
                firewalls_info.append((fw_name, blocked_list))

        with open(txt_output_path, "w", encoding="utf-8") as f:
            fw_index = 1
            for (fw_name, blocked_rules) in firewalls_info:
                f.write(f"Firewall {fw_index}\n")
                if not blocked_rules:
                    f.write("\n")
                    fw_index += 1
                    continue

                for (fwN, src, dst, proto, prt) in blocked_rules:
                    line = f"<{fwN} {src} {dst} {proto} {prt}>\n"
                    f.write(line)
                f.write("\n")
                fw_index += 1

    except Exception as e:
        # Debug isključiti u produkciji
        print(f"Greška: {e}")
        pass


class FileChangeHandler(FileSystemEventHandler):
    """Prati izmjene u XML datoteci i pokreće obradu."""
    def process_file(self):
        extract_blocked_and_group(XML_FILE_PATH, OUTPUT_FILE_PATH)

    def on_modified(self, event):
        if event.src_path == WATCHED_FILE:
            self.process_file()

    def on_created(self, event):
        if event.src_path == WATCHED_FILE:
            self.process_file()


def main():
    folder_to_watch = os.path.dirname(WATCHED_FILE)
    observer = Observer()
    event_handler = FileChangeHandler()
    observer.schedule(event_handler, path=folder_to_watch, recursive=False)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
