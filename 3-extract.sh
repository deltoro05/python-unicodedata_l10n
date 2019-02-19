if [ -f master.zip ]; then
    if [ -d unicode-table-data-master ]; then
        rm -rf unicode-table-data-master
    fi
    unzip master.zip
    rm -f master.zip
else
    echo 'ERROR: File master.zip not found. Please, try tunning 2-download.sh first.'
    exit 1
fi
