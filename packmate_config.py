#!/usr/bin/env python3

import os.path
from contextlib import suppress
from os import getenv

import requests
import yaml
from dotenv import load_dotenv

from git_deploy import get_docker_compose
from git_deploy import get_services

load_dotenv()
LOCAL_BASE_PATH = getenv("LOCAL_BASE_PATH", "/root/")
PASSWORD = getenv("PACKMATE_PASSWORD", "unimore")
USERNAME = getenv("PACKMATE_USERNAME", "unimore")
VULNBOX_IP = getenv("VULNBOX_IP", "10.60.0.1")
FLAG_REGEX = getenv("PACKMATE_FLAG_REGEX", "[A-Za-z0-9]\{31\}=")
print(f"{USERNAME}, {PASSWORD}, {VULNBOX_IP}, {FLAG_REGEX}")

URL = "http://" + VULNBOX_IP + ":65000"

def main():
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)

    ret = session.post(URL + "/api/pattern/", json={"actionType":"FIND", "color":"#FF7474", "directionType":"BOTH", "name":"FLAG", "searchType":"REGEX", "serviceId":None, "value":FLAG_REGEX})
    print(f"Pattern creation status: {ret.status_code}")
    dirs = get_services(LOCAL_BASE_PATH)
    for dir_path in dirs:
        docker_compose = get_docker_compose(dir_path)
        if not docker_compose.is_file(): continue

        with open(docker_compose, 'r') as f:
            content = f.read()
            compose_yaml = yaml.safe_load(content.strip())

        with suppress(Exception):
            servizi = compose_yaml.get('services', {})
            print(f"Trovati {len(servizi)} servizi in {os.path.split(dir_path)[1]}")

            for nome_servizio, config_servizio in servizi.items():
                port_mappings = config_servizio.get('ports', [])
                if not port_mappings: continue

                for port_mapping in port_mappings:
                    port = port_mapping.split(':')[-2]
                    resp = session.post(URL + "/api/service/", json={"name": os.path.split(dir_path)[1] + " " + nome_servizio, "port": port})
                    print(f"{os.path.split(dir_path)[1]} {nome_servizio} -> {port}")



if __name__ == "__main__": main()
