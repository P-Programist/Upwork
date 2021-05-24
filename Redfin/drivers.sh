# Define Absolute Path
SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

# Install drivers via Brew
brew install --cask chromedriver
brew install wget
brew install unzip
/usr/bin/safaridriver --enable

# Install Chromedriver
wget https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_mac64.zip -P /Users/umairrizwan/Downloads/Redfin/
unzip /Users/umairrizwan/Downloads/Redfin/chromedriver_mac64.zip -d /Users/umairrizwan/Downloads/Redfin/
rm /Users/umairrizwan/Downloads/Redfin/chromedriver_mac64.zip
cp /Users/umairrizwan/Downloads/Redfin/chromedriver /usr/local/bin

wget http://selenium-release.storage.googleapis.com/2.41/selenium-server-standalone-2.41.0.jar -P /Users/umairrizwan/Downloads/Redfin/

pip3 install -r /Users/umairrizwan/Downloads/Redfin/requirements.txt