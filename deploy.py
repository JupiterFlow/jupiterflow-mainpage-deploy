import requests
import os
import json
import pysftp


def put_dir_rec(local_folder, remote_folder):
    with pysftp.cd(local_folder):
        sftp.cwd(remote_folder)
        for folderItem in os.listdir('.'):
            if os.path.isfile(os.path.join(local_folder, folderItem)):
                print("fileUpload :", os.path.join(local_folder, folderItem))
                sftp.put(os.path.join(local_folder, folderItem), '%s/%s' % (remote_folder, folderItem),
                         preserve_mtime=True)
            else:
                if not sftp.exists('%s/%s' % (remote_folder, folderItem)):
                    sftp.mkdir('%s/%s' % (remote_folder, folderItem))
                put_dir_rec(os.path.join(local_folder, folderItem), '%s/%s' % (remote_folder, folderItem))


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

    put_dir_rec(os.path.join(os.getcwd(), 'data'), '/home/jupiterflow/app/mainpage/data')
