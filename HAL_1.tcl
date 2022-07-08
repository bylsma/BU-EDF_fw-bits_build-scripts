source ${BD_PATH}/HAL.tcl

if { [file isfile ${apollo_root_path}/configs/${build_name}/HAL_1.yaml] } {
    puts "Building HAL layer 1 for ${build_name}"
    BuildHAL ${apollo_root_path}/configs/${build_name}/HAL_1.yaml
}
