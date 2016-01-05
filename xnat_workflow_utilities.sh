# 
# Prerequisites:
#   XNAT_UTILS_HOME must be set
#

# Show information about a specified XNAT Workflow
xnat_workflow_show()
{
	local server=${1}
	local username=${2}
	local password=${3}
	local workflow_id=${4}

	${XNAT_UTILS_HOME}/xnat_workflow_info \
		--server=${server} \
		--username=${username} \
		--password=${password} \
		--workflow-id=${workflow_id} \
		show
}

# Update information (step id, step description, and percent complete)
# for a specified XNAT Workflow
xnat_workflow_update()
{
	local server=${1}
	local username=${2}
	local password=${3}
	local workflow_id=${4}
	local step_id=${5}
	local step_desc=${6}
	local percent_complete=${7}

	echo ""
	echo ""
	echo "---------- Step: ${step_id} "
	echo "---------- Desc: ${step_desc} "
	echo ""
	echo ""

	echo "xnat_workflow_update - workflow_id: ${workflow_id}"
	echo "xnat_workflow_update - step_id: ${step_id}"
	echo "xnat_workflow_update - step_desc: ${step_desc}"
	echo "xnat_workflow_update - percent_complete: ${percent_complete}"

	${XNAT_UTILS_HOME}/xnat_workflow_info \
		--server="${server}" \
		--username="${username}" \
		--password="${password}" \
		--workflow-id="${workflow_id}" \
		update \
		--step-id="${step_id}" \
		--step-description="${step_desc}" \
		--percent-complete="${percent_complete}"
}

# Mark the specified XNAT Workflow as complete
xnat_workflow_complete()
{
	local server=${1}
	local username=${2}
	local password=${3}
	local workflow_id=${4}

	${XNAT_UTILS_HOME}/xnat_workflow_info \
		--server="${server}" \
		--username="${username}" \
		--password="${password}" \
		--workflow-id="${workflow_id}" \
		complete
}

# Mark the specified XNAT Workflow as failed
xnat_workflow_fail()
{
	local server=${1}
	local username=${2}
	local password=${3}
	local workflow_id=${4}

	${XNAT_UTILS_HOME}/xnat_workflow_info \
		--server="${server}" \
		--username="${username}" \
		--password="${password}" \
		--workflow-id="${workflow_id}" \
		fail
}

# Update specified XNAT Workflow to Failed status and exit this script
die()
{
	xnat_workflow_fail ${1} ${2} ${3} ${4}
	exit 1
}
