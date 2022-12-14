#!/bin/bash
usage() {
echo "Usage: RunInApptainer.sh WorkingDirectory ProjectName"
    exit 0
    }

while getopts n:w:s:l:d:p:e:o:rh opt
do
    case "${opt}" in
	h|*) usage;;
    esac
done

#APPTAINER_IMAGE="/Data/images/Ubuntu_18.04_Apollo_Vivado2020.2.sif"
#SING_HOME="/home/SM_ZYNQ_FW"
#SINGULARITYENV_LM_LICENSE_FILE=2112@licenxilinx
#PROJ=rev2a_xczu7ev
[[ -z $LM_LICENSE_FILE ]] && [[ -z $APPTAINERENV_LM_LICENSE_FILE ]] && \
    echo 'ERROR: LM_LICENSE_FILE Vivado Licence file has not been defined' && \
    echo 'INFO: you could "export LM_LICENSE_FILE" or hardcode it in build-scripts/RinInApptainer' && \
    exit
[[ -z $APPTAINER_IMAGE ]] && \
    echo 'ERROR: APPTAINER_IMAGE has not been defined' && \
    echo 'INFO: you could "export APPTAINER_IMAGE" or hardcode it in build-scripts/RinInApptainer' && \
    exit
[[ -z $2 ]] && \
    echo 'ERROR: you need to specify a working directory and a project to build' && \
    exit


[[ -z $APPTAINERENV_LM_LICENSE_FILE ]] && \
    echo not defined &&\
    APPTAINERENV_LM_LICENSE_FILE=$LM_LICENSE_FILE
#keeping singularity for backward compatibility
SINGULARITYENV_LM_LICENSE_FILE=$APPTAINERENV_LM_LICENSE_FILE
SING_HOME=$1
PROJ=$2

singularity  exec -H $SING_HOME $APPTAINER_IMAGE /bin/bash -c "unset which; make BUILD_VIVADO_VERSION=2020.2 BUILD_VIVADO_BASE=/opt/Xilinx/Vivado $PROJ"
