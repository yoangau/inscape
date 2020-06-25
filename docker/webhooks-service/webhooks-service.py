from flask import request, Flask, render_template_string, abort, g
import yaml
from waitress import serve
import subprocess
import hmac
from hashlib import sha1
from threading import Thread


def read_config():
    with open('config.yml', 'r') as config_file:
        return yaml.load(config_file, Loader=yaml.FullLoader)


app = Flask(__name__)
config = read_config()


def create_env(service, env):
    with open(f"../{service}/.env", 'w') as env_file:
        content = [f'{name.upper()}={value}\n' for name,
                   value in env.items()]
        env_file.writelines(content)


def start_docker(service):
    service_path = f"../{service}"
    subprocess.run("docker-compose up -d", cwd=service_path,
                   shell=True, capture_output=True)


def stop_docker(service):
    service_path = f"../{service}"
    subprocess.run("docker-compose down", cwd=service_path,
                   shell=True, capture_output=True)


def change_image(service, image):
    env = config['services'][service]['env']
    env['image_name'] = image
    create_env(service, env)


def get_image_name(json):
    package = json['package']
    base_url = package['registry']['url'].split('//')[-1]
    package_name = package['name']
    package_version = package['package_version']['version']
    return f'{base_url}/{package_name}:{package_version}'


class RollUpdate(Thread):
    def __init__(self, service, image):
        Thread.__init__(self)
        self.service = service
        self.image = image

    def run(self):
        stop_docker(self.service)
        change_image(self.service, self.image)
        start_docker(self.service)


def init_network(network_name):
    subprocess.run(f'docker network create {network_name}',
                   shell=True, capture_output=True)


@app.route('/package/<service>', methods=['POST'])
def handle_package_webhook(service):
    if "X-Hub-Signature" not in request.headers:
        abort(403)
    signature = request.headers.get("X-Hub-Signature", "").split("=")[1]

    mac = hmac.new(config['services'][service]['secret'].encode('utf-8'),
                   msg=request.data, digestmod=sha1)
    if not str(mac.hexdigest()) == str(signature):
        abort(403)

    image = get_image_name(request.get_json())

    thread = RollUpdate(service, image)
    thread.start()

    return render_template_string(image), 200


if __name__ == '__main__':
    init_network(config['network'])
    for service, value in config['services'].items():
        stop_docker(service)
        create_env(service, value['env'])
        start_docker(service)
    serve(app, host="0.0.0.0", port=config['port'])
