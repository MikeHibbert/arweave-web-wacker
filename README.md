# Arweave WebWacker
Automated Data Archiver to Arweave permaweb

## Install

1) create a virtualenv and clone the code into the env:
```
virtualenv --no-site-packages -p python3.6 web-whacker
cd web-whacker
source bin/activate
clone https://github.com/MikeHibbert/arweave-web-wacker.git
```

2) install dependencies
```
cd arweave-web-wacker
pip install -r requirements.txt
```

3) Run the program with your url that you want backup into the blockchain (depth is optional):
```
python bot.py <root URL> <path to your wallet file> <depth>
```

NOTE: a project file with the urls name and timestamp is created so you can monitor submission to the blockchain

### Status checking
You can use the check_project_status.py to check the current status of the project created:
```
python check_project_status.py "<wallet file path>" "<project file path>"
