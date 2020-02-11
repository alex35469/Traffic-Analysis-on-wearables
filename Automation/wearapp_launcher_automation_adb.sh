#!/bin/bash

# Simulation of applications oppenning and closing
# Does not need monkeyrunner

##### PARAMETERS

# Read file
APPLIS=`cat app-pack.csv`

# Inter application sleeping time
SLEEPINGTIMER=15

# Time needed to clean and close the App
CLOSING_TIME=5

# Device to which send the command
MAIN_DEVICE=192.168.1.134:5555

# nb of time to perform the action for each device
REPEAT=20

LOGDIR="logs"

if [ ! -d "$LOGDIR" ]; then
    mkdir $LOGDIR
fi


##### FUNCTIONS
function openApp()
{
APP=$1
ACTIVITY=$2
DEVICE=$3
adb -s $DEVICE shell am start -c api.android.intent.LAUNCHER -a api.android.category.MAIN -n $APP/$ACTIVITY
}

function closeApp()
{
APP=$1
DEVICE=$2
adb -s $DEVICE shell pm clear $APP
}


##### MAIN
# Clear the logcat
adb -s $MAIN_DEVICE logcat -c

RECORDS=""
echo "Start openning applications"
IFS=$'\n'
for line in $APPLIS
do
    NAME=$(echo $line | awk -F, '{print $1}')
    APP=$(echo $line | awk -F, '{print $2}')
    ACTIVITY=$(echo $line | awk -F, '{print $3}')
    if [[ $NAME == !* ]]; then
        continue
    fi

    for ((i=1;i<=REPEAT;i++))
        do

            echo "Recording: $NAME $i"

            NOWOPEN=$(date +"%Y-%m-%d %H:%M:%S")
            # Launch Application
            openApp $APP $ACTIVITY $MAIN_DEVICE

            # let the app exchange somme data
            sleep $SLEEPINGTIMER

            NOWCLOSE=$(date +"%Y-%m-%d %H:%M:%S")

            # Clean and close the app
            closeApp $APP $MAIN_DEVICE

            sleep $CLOSING_TIME

            RECORDS="${RECORDS}${NAME} ${i} ${NOWOPEN} ${NOWCLOSE}\n"
        done
done


now=$(date +"%Y-%m-%d %H:%M:%S")
model=$(adb devices -l | grep $MAIN_DEVICE | cut -d ' ' -f 8 | cut -d ':' -f 2)
LNAME="$model $now logcat.txt"
TNAME="$model $now logtime.txt"

# save logcat
LOGCATOUTPUT="$LOGDIR/$LNAME"
if [ ! -d "$LOGCATOUTPUT" ]; then
    touch "$LOGCATOUTPUT"
fi

./adb -s $MAIN_DEVICE logcat -d > "$LOGCATOUTPUT"
echo -en "\n\n" >> "$LOGCATOUTPUT"

# save logtime
TIMEOUTPUT="$LOGDIR/$TNAME"
if [ ! -d "$TIMEOUTPUT" ]; then
touch "$TIMEOUTPUT"
fi
echo -en $RECORDS > "$TIMEOUTPUT"
echo -en "\n\n" >> "$TIMEOUTPUT"
