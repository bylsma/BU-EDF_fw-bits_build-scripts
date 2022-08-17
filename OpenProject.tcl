global apollo_root_path
global BD_PATH
set apollo_root_path ../
set BD_PATH ${apollo_root_path}/bd/

if {$argc == 3} {
    set build_name [lindex $argv 2]
    set build_scripts_path [lindex $argv 1]
    set apollo_root_path [lindex $argv 0]
    set autogen_path configs/${build_name}/autogen
} elseif {$argc == 2} {
    set build_scripts_path [lindex $argv 1]
    set apollo_root_path [lindex $argv 0]
} elseif {$argc == 1} {
    set apollo_root_path [lindex $argv 0]
    set build_scripts_path ${apollo_root_path}/build-scripts
} else {
    set apollo_root_path ".."
    set build_scripts_path ${apollo_root_path}/build-scripts
}

set BD_PATH ${apollo_root_path}/bd
