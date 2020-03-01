import requests
import os
import json
import pysftp


def put_r_portable(sftp_self, localdir, remotedir, preserve_mtime=False):
    for entry in os.listdir(localdir):
        remotepath = remotedir + "/" + entry
        localpath = os.path.join(localdir, entry)
        if not os.path.isfile(localpath):
            try:
                sftp_self.mkdir(remotepath)
            except OSError:
                pass
            put_r_portable(sftp_self, localpath, remotepath, preserve_mtime)
        else:
            print("fileUpload :", localpath)
            sftp_self.put(localpath, remotepath, preserve_mtime=preserve_mtime)


with open('_config/configure.json') as f:
    configureData = json.load(f)

sftp_hostname = configureData["sftp"]["host"]
sftp_username = configureData["sftp"]["user"]
sftp_privkey = configureData["sftp"]["privKey"]

ROOT_PATH = configureData["global"]["ROOT_PATH"]

with open(os.path.join(ROOT_PATH, 'data.json'), 'r', encoding='UTF8') as f:
    json_data = json.load(f)
projectData = json_data["content"]["project"]["data"]

for idx, project in enumerate(projectData):
    if project["markdown"]:
        r = requests.get(project["markdown"])
        txt = r.text
    else:
        txt = configureData["global"]["MARKDOWN_EMPTY"]

    markdownPath = os.path.join(ROOT_PATH, 'project', str(idx + 1))
    try:
        if not (os.path.isdir(markdownPath)):
            os.makedirs(os.path.join(markdownPath))
    except OSError as e:
        if e.errno != OSError.EEXIST:
            print("Failed to create directory!!!!!")
            raise

    f = open(os.path.join(markdownPath, "README.md"), mode='wt', encoding='utf-8')
    f.write(txt)

    print("=================================================================")
    print(idx + 1, project["subject"], "::", "README 생성 완료")
    print("=================================================================")

    f.close()

with pysftp.Connection(host=sftp_hostname, username=sftp_username, private_key=sftp_privkey) as sftp:
    print("Connection succesfully stablished ... ")
    put_r_portable(sftp, os.path.join(os.getcwd(), 'data'), '/home/jupiterflow/app/mainpage/data', True)
