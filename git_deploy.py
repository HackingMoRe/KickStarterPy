import os
import subprocess
from pathlib import Path
import yaml

LOCAL_BASE_PATH = "root"


def create_ignore(folder_path):
    docker_compose = Path(os.path.join(folder_path, "docker-compose.yml"))
    if docker_compose.is_file():
        print(f"Trovato docker-compose.yaml in {folder_path}")

        git_ignore = Path(os.path.join(folder_path, ".gitignore"))
        with open(git_ignore, 'a') as f_ignore:
            with open(docker_compose, 'r') as f:
                compose_yaml = yaml.safe_load(f)

            volumi = compose_yaml.get('volumes', {})
            if volumi:
                for nome_volume in volumi:
                    f_ignore.write(f"\n{nome_volume.split(':')[0]}")

            servizi = compose_yaml.get('services', {})
            for _, config_servizio in servizi.items():
                volumi_servizio = config_servizio.get('volumes', [])
                if volumi_servizio:
                    for nome_volume in volumi_servizio:
                        f_ignore.write(f"\n{nome_volume.split(':')[0]}")


def initialize_and_push(folder_path):  # def initialize_and_push(folder_path, github_repo_url):
    try:
        # subprocess.run(["git", "config", "--global http.postBuffer 1048576000"], cwd=folder_path, check=True)
        subprocess.run(["git", "config", "--global", "user.name", "git_deploy.py"], cwd=folder_path, check=True)
        subprocess.run(["git", "config", "--global", "user.email", "git_deploy"], cwd=folder_path, check=True)
        subprocess.run(["git", "init"], cwd=folder_path, check=True)
        subprocess.run(["git", "add", "."], cwd=folder_path, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=folder_path, check=True)

        print(f"[↑] Creato repository {folder_path}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Errore in {folder_path}: {e}")


for item in os.listdir(LOCAL_BASE_PATH):
    item_path = os.path.join(LOCAL_BASE_PATH, item)
    create_ignore(item_path)
    print(f"📁 Trovata cartella: {item}")
    initialize_and_push(item_path)
