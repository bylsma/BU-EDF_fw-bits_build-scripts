#################################################################################
# make stuff
#################################################################################
SHELL=/bin/bash -o pipefail

#add path so build can be more generic
MAKE_PATH := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

ifeq (, $(shell which ccze 2> /dev/null))
  CCZE_CMD=
else
  CCZE_CMD=| ccze -A
endif 
OUTPUT_MARKUP= 2>&1 | tee -a ../make_log.txt ${CCZE_CMD}
SLACK_MESG ?= echo

all:
	@echo "Please specify a design to build"
	echo '${OUTPUT_MARKUP}'
	@$(MAKE) list 

clean_make_log:
	@rm -f make_log.txt &> /dev/null

#################################################################################
# Slack notifications
#################################################################################
NOTIFY_DAN_GOOD:
	${SLACK_MESG} "FINISHED building FW!"
NOTIFY_DAN_BAD:
	${SLACK_MESG} "FAILED to build FW!"
	false

#################################################################################
# Help 
#################################################################################

#list magic: https://stackoverflow.com/questions/4219255/how-do-you-get-the-list-of-targets-in-a-makefile
#all grep commands need || true because not finding a match is an error and breaks the make rule
list:
	@echo
	@echo Build config:
	@$(MAKE) -pRrq -f $(MAKEFILE_LIST) | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep rev[[:digit:]] || true | grep -v prebuild || true | grep -v clean || true | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' || true | column -c 150
	@echo
	@echo Prebuilds:
	@$(MAKE) -pRrq -f $(MAKEFILE_LIST) | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep prebuild_ || true | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'  || true  | column -c 150
	@echo
	@echo Vivado:
	@$(MAKE) -pRrq -f $(MAKEFILE_LIST) | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep open_  || true | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'  || true | column -c 150
	@echo
	@echo Clean:
	@$(MAKE) -pRrq -f $(MAKEFILE_LIST) | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep clean_  || true | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'  || true | column -c 150
	@echo

full_list:
#	@$(MAKE) -pRrq -f $(MAKEFILE_LIST) 
	@$(MAKE) -pRrq -f $(MAKEFILE_LIST) | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' || true | column 
