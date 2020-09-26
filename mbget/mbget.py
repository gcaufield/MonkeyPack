from github import Github
import requests
import re

BARREL_FILE = re.compile(r'^.+\.barrel$')

def main():
    g = Github()
    repo = g.get_repo('gcaufield/MonkeyInject')


    for r in repo.get_releases():
        print(r.tag_name)
        for a in r.get_assets():
            print(a.name + " " + a.url + " " + a.content_type)
            if BARREL_FILE.match(a.name) != None:
                # Found a barrel file, Download it.
                headers = {'Accept': 'application/octet-stream'}
                r = requests.get(a.url, headers=headers)
                with open('./dl/' + a.name, 'wb') as f:
                    f.write(r.content)

if __name__ == "__main__":
    main()



