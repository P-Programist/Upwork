# Define Absolute Path
SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

# Install drivers via Brew
brew install --cask chromedriver
brew install wget
brew install unzip
/usr/bin/safaridriver --enable

# Install Chromedriver
wget https://chromedriver.storage.googleapis.com/91.0.4472.19/chromedriver_mac64.zip -P $SCRIPTPATH
unzip $SCRIPTPATH/chromedriver_mac64.zip -d $SCRIPTPATH/
rm $SCRIPTPATH/chromedriver_mac64.zip
cp $SCRIPTPATH/chromedriver /usr/local/bin

wget http://selenium-release.storage.googleapis.com/2.41/selenium-server-standalone-2.41.0.jar -P $SCRIPTPATH

