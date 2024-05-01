import os
import subprocess
import json

log_file = "error_log.txt"

def log_error(message):
    with open(log_file, "a") as f:
        f.write("Error: {}\n".format(message))

result = subprocess.run(["az", "devops", "project", "list", "--output", "json"], capture_output=True, text=True)
if result.returncode != 0:
    log_error("Error al obtener la lista de proyectos: {}".format(result.stderr))
    exit()

projects_data = json.loads(result.stdout)
os.makedirs("repositories", exist_ok=True)
os.chdir("repositories")

for project in projects_data["value"]:
    project_name = project["name"].replace("-", "_")
    os.makedirs(project_name, exist_ok=True)
    os.chdir(project_name)

    result = subprocess.run(["az", "repos", "list", "--project", project["name"], "--output", "json"], capture_output=True, text=True)
    if result.returncode != 0:
        log_error("Error al obtener la lista de repositorios para el proyecto {}: {}".format(project["name"], result.stderr))
        os.chdir("..")
        continue

    repos_data = json.loads(result.stdout)

    for repo in repos_data:
        repo_name = os.path.basename(repo["sshUrl"]).replace(".git", "")
        result = subprocess.run(["git", "clone", repo["sshUrl"], repo_name], capture_output=True, text=True)
        if result.returncode != 0:
            log_error("Error al clonar el repositorio {} en el proyecto {}: {}".format(repo_name, project_name, result.stderr))

    os.chdir("..")
