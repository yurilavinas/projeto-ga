#!/bin/tcsh

#
# Run daily Dispatcher for five-year models generation and evaluation
#

source ~/.tcshrc

set year=`date '+%Y'`
# Don't pad integer values with zero's
set month=`date '+%_m'`
set day=`date '+%_d'`

# Pad time values with zero's
set hour=`date '+%H'`
set min=`date '+%M'`
set sec=`date '+%S'`


# Capture all output produced by Dispatcher into the daily log file
set logdir=$CSEP/dispatcher/logs/"$year"_"$month"
mkdir -p "$logdir"

set logfile="$logdir"/five_year_"$year-$month-$day-$hour$min$sec"


# Invoke Dispatcher for "today" (with 31 day delay for the testing date):
nohup python $CENTERCODE/src/generic/Dispatcher.py --year="$year" --month="$month" --day="$day" --configFile=$CSEP/cronjobs/dispatcher_five_year.init.xml --waitingPeriod=31 --disableMatlabDisplay --enableForecastXMLTemplate --enableForecastMap --publishServer=csep-usc@intensity.usc.edu --publishDirectory=/var/www/html/csep/data/us/usc/california --logFile="$logfile" >& "$logfile" &


