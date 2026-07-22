from dpnael.services.docker_service import DockerService
from dpnael.ui.app import DpnaelApp

def main():
    docker_service = DockerService()
    app = DpnaelApp(docker_service=docker_service)
    app.run()

if __name__ == "__main__":
    main()