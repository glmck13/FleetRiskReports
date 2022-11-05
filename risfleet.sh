#!/bin/ksh

. ~/etc/risopts.conf

risfleet.py $INTERVAL >$OUTFILE
sendaway.sh "$REPORT" "Fleet Management Report" "See attached" $OUTFILE

END=$(date "+%a, %b-%d-%Y")
BEGIN=$(date --date="today-${INTERVAL}days" "+%a, %b-%d-%Y")

grep DRIVER $OUTFILE | sed -e 's/<!--//' -e 's/-->//' -e 's/<[^>]*>/|/g' -e 's/||*/|/g' -e 's/&nbsp;//g' -e 's/ *DRIVER *//' |
while IFS='|' read x NAME speed harsh policy EMAIL
do
	speed+="+" harsh+="+" policy+="+"

	TABLE=""
	while read rule
	do
	name=${rule##*,} rule=${rule%,*} subtype=${rule##*,} rule=${rule%,*}

	case "$subtype" in
	Speeding)
		count=${speed%%+*} speed=${speed#*+}
		;;
	Harsh\ Driving)
		count=${harsh%%+*} harsh=${harsh#*+}
		;;
	Policy\ Issue)
		count=${policy%%+*} policy=${policy#*+}
		;;
	*)
		count=0
		;;
	esac
	[ "$count" -gt 0 ] && TABLE+="\t$name: $count\n"

	done <$RULES

	#print $NAME $EMAIL
	#print $TABLE

	MESSAGE=$(cat "$NOTICE" | sed -e "s/%BEGIN%/$BEGIN/" -e "s/%END%/$END/" -e "s/%NAME%/${NAME#*, }/" -e "s/%TABLE%/$TABLE/" -e "s/%MAILTO%/$MAILTO/" | tr '\n' '\r')

	sendaway.sh "$EMAIL" "Driving Exception Notice" "$MESSAGE"
	sleep 30
done
