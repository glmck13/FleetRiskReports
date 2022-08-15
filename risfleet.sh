#!/bin/ksh

. ~/etc/risopts.conf

risfleet.py $INTERVAL >$OUTFILE
sendaway.sh "$REPORT" "Fleet Management Report" "See attached" $OUTFILE

END=$(date "+%a, %b-%d-%Y")
BEGIN=$(date --date="today-${INTERVAL}days" "+%a, %b-%d-%Y")

grep DRIVER $OUTFILE | sed -e 's/<!--//' -e 's/-->//' -e 's/<[^>]*>/|/g' -e 's/||*/|/g' -e 's/&nbsp;//g' -e 's/ *DRIVER *//' |
while IFS='|' read x NAME speed harsh belt EMAIL
do
	print ${speed//+/ } | read SPEED75 SPEED15 SPEED15LONG
	print ${harsh//+/ } | read ACCEL BRAKING CORNERING
	print ${belt//+/ } | read BELT
	#print $NAME, $SPEED75, $SPEED15, $SPEED15LONG, $ACCEL, $BRAKING, $CORNERING, $BELT, $EMAIL

	TABLE=""
	[ "$SPEED75" -gt 0 ] && TABLE+="\tSpeed >75MPH: "$SPEED75"\n"
	[ "$SPEED15" -gt 0 ] && TABLE+="\tSpeed >15MPH over posted limit: "$SPEED15"\n"
	[ "$SPEED15LONG" -gt 0 ] && TABLE+="\tSpeed >15MPH over posted limit for >20secs: "$SPEED15LONG"\n"
	[ "$ACCEL" -gt 0 ] && TABLE+="\tRapid acceleration: "$ACCEL"\n"
	[ "$BRAKING" -gt 0 ] && TABLE+="\tHard braking: "$BRAKING"\n"
	[ "$CORNERING" -gt 0 ] && TABLE+="\tAggressive turn: "$CORNERING"\n"
	[ "$BELT" -gt 0 ] && TABLE+="\tNo seat belt: "$BELT"\n"

	EMAIL=$MAILTO
	print $EMAIL
	MESSAGE=$(cat "$NOTICE" | sed -e "s/%BEGIN%/$BEGIN/" -e "s/%END%/$END/" -e "s/%NAME%/${NAME#*, }/" -e "s/%TABLE%/$TABLE/" -e "s/%MAILTO%/$MAILTO/" | tr '\n' '\r')

	sendaway.sh "$EMAIL" "Driving Exception Notice" "$MESSAGE"
done
