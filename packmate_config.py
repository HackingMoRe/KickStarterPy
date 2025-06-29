import os.path
from contextlib import suppress
from os import getenv

import requests
import yaml
from dotenv import load_dotenv

from git_deploy import get_docker_compose
from git_deploy import get_services

load_dotenv()
LOCAL_BASE_PATH = getenv("LOCAL_BASE_PATH")
PASSWORD = getenv("PACKMATE_PASSWORD")
USERNAME = getenv("PACKMATE_USERNAME")
URL = getenv("PACKMATE_URL")
FLAG_REGEX = getenv("PACKMATE_FLAG_REGEX")


def main():
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)

    session.post(URL + "/api/pattern/", json={"actionType":"FIND", "color":"#FF7474", "directionType":"BOTH", "name":"FLAG", "searchType":"REGEX", "serviceId":None, "value":FLAG_REGEX})
    
    dirs = get_services(LOCAL_BASE_PATH)
    for dir_path in dirs:
        docker_compose = get_docker_compose(dir_path)
        if not docker_compose.is_file(): continue

        with open(docker_compose, 'r') as f:
            content = f.read()
            compose_yaml = yaml.safe_load(content.strip())

        with suppress(Exception):
            servizi = compose_yaml.get('services', {})

            for nome_servizio, config_servizio in servizi.items():
                porte = config_servizio.get('ports', [])
                if not porte: continue

                for porta in porte:
                    session.post(URL + "/api/service/", json={"name": os.path.split(dir_path)[1] + " " + nome_servizio, "port": porta.split(':')[0]})
                    # print(f"{os.path.split(dir_path)[1]} {nome_servizio} -> {porta.split(':')[0]}")



if __name__ == "__main__": main()
