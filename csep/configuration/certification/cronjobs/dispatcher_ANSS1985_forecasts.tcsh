#!/bin/tcsh

# dispatcher_ANSS1985.csh:
#
# Run daily Dispatcher for Califonia one-day and RELM forecast models generation
# and evaluation
# (all groups are using the same input ANSS catalog with start date of 1985-01-01
#  and minimum magnitude threshold of 3.0)
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

set logfile="$logdir"/dailyANSS1985forecasts_"$year-$month-$day-$hour$min$sec"


# Invoke Dispatcher for "today" (with 31 day delay for the testing date):
nohup python $CENTERCODE/src/generic/Dispatcher.py --year="$year" --month="$month" --day="$day" --tests=" " --configFile=$CSEP/cronjobs/dispatcher_ANSS1985_forecasts.init.xml --waitingPeriod=31 --enableForecastXMLTemplate --enableForecastMap --logFile="$logfile" >& "$logfile" &


