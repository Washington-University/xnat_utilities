#!/bin/bash

if [ -z "${SUBJECT_FILES_DIR}" ]; then
	echo "Environment variable SUBJECT_FILES_DIR must be set!"
	exit 1
fi

check_project=${1}

if [ -z "${check_project}" ]; then
	echo "Please specify project to check as first parameter to a call to this utility"
	exit 1
fi

rm ${check_project}.subjects
touch ${check_project}.subjects
rm ${check_project}.not.subjects
touch ${check_project}.not.subjects

subject_file_name="${SUBJECT_FILES_DIR}/DetermineIfSubjectInProject.subjects"
echo "Retrieving subject list from: ${subject_file_name}"
subject_list_from_file=( $( cat ${subject_file_name} ) )
subjects="`echo "${subject_list_from_file[@]}"`"

for subject in ${subjects} ; do
	echo "Checking Subject: ${subject}"
	if [ -d "/HCP/hcpdb/archive/${check_project}/arc001/${subject}_3T" ] ; then
		echo "${subject} is in ${check_project}"
		echo ${subject} >> ${check_project}.subjects
	else
		echo "${subject} is NOT in ${check_project}"
		echo ${subject} >> ${check_project}.not.subjects
	fi
done