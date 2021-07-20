#!/bin/bash
# Author: Giovanni Paiva (paivagio@hotmail.com)

# ------------- Wrapper for CliNTREc -------------

# ATTENTION: Read the usage guideline on https://github.com/paivagio/CliNTREc and
# change/fill only the fields needed for the task you want to run. If you are not 
# using a field any longer leave it blank. 

INPUT_FOLDER=''       	# -i  (DEFAULT: temp)
OUTPUT_FOLDER=''      	# -o  (DEFAULT: temp)
FILENAME_EC=''      	# -t  (DEFAULT: ec.txt)
ID_TRIAL=''             # -id (DEFAULT: None)
FILENAME_EHR=''         # -e  (DEFAULT: None)
COHORT_SELECTION=''  	# -s  (DEFAULT: False)

# ------------- COMMAND GENERATOR -------------

if [ "x$INPUT_FOLDER" == "x"  ]; then
    I=''
else
	I='-i $INPUT_FOLDER'
fi

if [ "x$OUTPUT_FOLDER" == "x"  ]; then
    O=''
else
	O='-o $OUTPUT_FOLDER'
fi

if [ "x$FILENAME_EC" == "x"  ]; then
    T=''
else
	T='-t $FILENAME_EC'
fi

if [ "x$ID_TRIAL" == "x"  ]; then
    ID=''
else
	ID='-id $ID_TRIAL'
fi

if [ "x$FILENAME_EHR" == "x"  ]; then
    E=''
else
	E='-e $FILENAME_EHR'
fi

if [ "x$COHORT_SELECTION" == "x"  ]; then
    S=''
else
	S='-s $COHORT_SELECTION'
fi

python main.py ${I} ${O} ${T} ${ID} ${E} ${S}

$SHELL