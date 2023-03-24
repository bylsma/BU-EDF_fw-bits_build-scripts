source -notrace ${apollo_root_path}/build-scripts/SetupHelper.tcl

# Non-project mode
# collect files
# run synthesis
set_param general.maxThreads 10


source ${apollo_root_path}/configs/${build_name}/settings.tcl
source ${build_scripts_path}/helpers/FW_info.tcl

#################################################################################
# STEP#0: define output directory area.
#################################################################################
file mkdir $outputDir

set projectDir ${apollo_root_path}/proj/
file mkdir $projectDir
if {[file isfile $projectDir/$top.xpr]} {
    puts "Re-creating project file."
} else {
    puts "Creating project file."
}
create_project -force -part $FPGA_part $top $projectDir
set_property target_language VHDL [current_project]
puts "Using dir $projectDir for FPGA part $FPGA_part"


#################################################################################
# STEP#1: setup design sources and constraints
#################################################################################

#build the build timestamp file
[build_fw_version ${apollo_root_path}/src $FPGA_part]
set timestamp_file ${apollo_root_path}/src/fw_version.vhd
read_vhdl ${timestamp_file}
puts "Adding ${timestamp_file}"


ProcessFileListFile ${apollo_root_path}/configs/${build_name}/files.tcl {}
