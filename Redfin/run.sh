# Define Absolute Path
SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

# $SCRIPTPATH/drivers.sh # Comment out this line

python3 $SCRIPTPATH/main.py