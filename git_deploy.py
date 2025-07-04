import os, re, yaml, glob
import subprocess
from contextlib import suppress
from os import getenv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
LOCAL_BASE_PATH = getenv("LOCAL_BASE_PATH")


def get_docker_compose(path):
    docker_compose_yml = glob.glob(os.path.join(path, "*compose.yml"))
    docker_compose_yaml = glob.glob(os.path.join(path, "*compose.yaml"))
    docker_compose = docker_compose_yml[0] if docker_compose_yml else docker_compose_yaml[0]
    return Path(docker_compose)


def create_ignore(folder_path):
    try: docker_compose = get_docker_compose(folder_path)
    except Exception: return
    
    if not docker_compose.is_file() or not docker_compose: return
    print(f"Trovato {docker_compose}")

    with open(docker_compose, 'r') as f:
        content = f.read()
        compose_yaml = yaml.safe_load(content.strip())

    git_ignore = Path(os.path.join(folder_path, ".gitignore"))
    ignore_dirs = set()

    with suppress(Exception):
        servizi = compose_yaml.get('services', {})

        for config_servizio in servizi.values():
            volumi_servizio = config_servizio.get('volumes', [])
            if not volumi_servizio: continue

            for nome_volume in volumi_servizio:
                bind_mnt = nome_volume.split(':')[0]

                if not bind_mnt.startswith("./") and not bind_mnt.startswith("/"): continue

                bind_mnt = re.sub(r'^./', r'', bind_mnt)
                bind_mnt = bind_mnt if bind_mnt.endswith("/") else bind_mnt + "/"
                ignore_dirs.add("\n" + bind_mnt)

    with open(git_ignore, 'a') as f_ignore:
        f_ignore.writelines(ignore_dirs)


def initialize(folder_path):
    try:
        subprocess.run(["git", "config", "--global", "user.name", "vulnbox"], cwd=folder_path, check=True)
        subprocess.run(["git", "config", "--global", "user.email", "vulnbox@cyberchallenge"], cwd=folder_path, check=True)
        subprocess.run(["git", "init"], cwd=folder_path, check=False)
        subprocess.run(["git", "add", "."], cwd=folder_path, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=folder_path, check=True)
        subprocess.run(["git", "branch", "backup"], cwd=folder_path, check=False)
        print(f"[↑] Creato repository {folder_path}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Errore in {folder_path}: {e}")


def get_services(base_path):
    with open("blacklist_git_deploy", 'r') as bf:
        blacklist = [line.strip() for line in bf]
        return filter(
            lambda x: (os.path.isdir(x) and not os.path.basename(x).startswith('.') and os.path.basename(x) not in blacklist),
            map(
                lambda d: os.path.join(base_path, d),
                os.listdir(base_path)
            )
        )


def main():
    print(LOCAL_BASE_PATH)
    dirs = get_services(LOCAL_BASE_PATH)

    for dir_path in dirs:
        create_ignore(dir_path)
        print(f"📁 Trovata cartella: {dir_path}")
        initialize(dir_path)


if __name__ == "__main__": main()
