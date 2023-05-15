#!/bin/bash

#Skrypt do pobierania danych z portalu "pvmonitor.pl"

WEB_HOST="https://pvmonitor.pl/inst_sumaax.php?i=0"

ID="$1"
START_DATE="$2"
END_DATE="$3"

OUTPUT_FILE="pv/${ID}_PVdata.csv"

function send_error () {
	echo "An error occurred..."
	case $1 in
		1)
			echo "Inproper use!"
            echo "Pattern:"
            echo -e "\n"
            echo "  <ID> <Start date> <End date>"
            echo -e "\n"
            echo "Example:"
            echo -e "\n"
            echo "  ./scrapper 10001 01-01-2023 31-12-2023"
            echo -e "\n"
			exit 1
			;;
		2)
			echo "Start date should be less than end date!"
			exit 1
			;;
		*)
			echo "Undefinied error!"
			exit 1
	esac
}

function execute_dates() {
    UNIX_START_DATE=$(date -d "$START_DATE" +%s)
    UNIX_END_DATE=$(date -d "$END_DATE" +%s)

    if [ $UNIX_START_DATE -gt $UNIX_END_DATE ]; then send_error 2; fi

    > $OUTPUT_FILE

    echo \"DateTime\",\"Moc chwilowa PV\" >> $OUTPUT_FILE

    for (( CURRENT_DATE=UNIX_START_DATE; CURRENT_DATE<=UNIX_END_DATE; CURRENT_DATE+=86400 )); do
        TMP_DATE=$(date -d @$CURRENT_DATE +%Y-%m-%d)
        
        DATA=$(curl -s "https://pvmonitor.pl/inst_sumaax.php?i=0&id=$ID&rodz=1&od=$TMP_DATE&do=$TMP_DATE&" -H 'sec-fetch-mode: cors' -H 'sec-fetch-site: same-origin' -H 'user-agent: Mozilla')

        REGEX="'Moc chwilowa PV', data:.\[{.*?}\]"

        REGEX_DATA=$(echo $DATA | grep -oP "$REGEX")

        REGEX_DATA=${REGEX_DATA#*"'Moc chwilowa PV', data: [{"}

        REGEX_DATA=${REGEX_DATA%%"}]"}

        REGEX_DATA=${REGEX_DATA//\}\,\{/;}

        IFS=';' read -ra ADDR <<< "$REGEX_DATA"
        for SAMPLE in "${ADDR[@]}"; do
            SAMPLE=${SAMPLE#*x:}

            UNIX_DATA=${SAMPLE%%,*}
            DAY=$(date -d @$(($UNIX_DATA / 1000)) +'%Y-%m-%d %H:%M:%S')

            month=$(date -d "$DAY" +"%m")
            month=${month#0}
            day=$(date -d "$DAY" +"%d")

            if (( (month == 3 && day >= 27) || (month > 3 && month < 10) || (month == 10 && day <= 29) )); then
                DAY=$(date -d "$DAY 2 hours ago" +"%Y-%m-%d %H:%M:%S")
            else
                DAY=$(date -d "$DAY 1 hours ago" +"%Y-%m-%d %H:%M:%S")
            fi

            VALUE=${SAMPLE#*",y:"} 

            echo \"$DAY\",$VALUE >> $OUTPUT_FILE
        done

        echo "[$TMP_DATE] Done"
    done
}


# SCRIPT START
if [ $# -ne 3 ]; then send_error 1; fi

execute_dates