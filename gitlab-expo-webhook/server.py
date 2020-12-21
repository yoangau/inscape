from sanic import Sanic
from sanic.response import text
import requests
import os

GITLAB_PRIVATE_TOKEN = os.environ.get("GITLAB_PRIVATE_TOKEN")
EXPO_PROJECT = os.environ.get("EXPO_PROJECT")
PORT = os.environ.get("PORT")
DEPLOY_PREFIX = os.environ.get("DEPLOY_PREFIX")
app = Sanic(__name__)


async def send_note(project_id, mr_iid):
    message = f"![Expo QR](https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=exp://exp.host/{EXPO_PROJECT}?release-channel={DEPLOY_PREFIX}--{mr_iid})"
    answer = requests.post(f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{mr_iid}/notes", json={
                           "body": message}, headers={"PRIVATE-TOKEN": GITLAB_PRIVATE_TOKEN, "Content-Type": "application/json"})
    print(answer)


@app.post("/")
async def merge_request_event(req):
    if (req.json['object_attributes']['action'] != "open"):
        return text("Nothing to do", status=200)
    mr_iid = req.json['object_attributes']['iid']
    project_id = req.json['project']['id']

    await send_note(project_id, mr_iid)

    return text("Merge request message create", status=200)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT, auto_reload=True)
