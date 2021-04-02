sudo apt-get install python3 -y
sudo apt-get install python3-dev -y
sudo apt-get install virtualenv -y
virtualenv ./myvenv --python=python3
. ./myvenvvenv/bin/activate
./myvenv/bin/pip install selenium==4.0.0.b2
./myvenv/bin/pip install webdriver-manager
./myvenv/bin/pip install python-dev-tools --upgrade
./myvenv/bin/pip install aiocsv
./myvenv/bin/pip install aiofiles
./myvenv/bin/pip install beautifulsoup4
python3 main.py