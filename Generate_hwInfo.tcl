source ${BD_PATH}/utils/vivado_version.tcl  

set hw_dir kernel/hw

##re-Add xdc files
#for {set j 0} {$j < [llength $xdc_files ] } {incr j} {
#    set filename "${apollo_root_path}/[lindex $xdc_files $j]"
#    read_xdc $filename
#    puts "Adding $filename"
#}

#create bit file
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
write_bitstream -force ${apollo_root_path}/bit/top_${build_name}.bit

#create hwdef file
write_hwdef -file ${apollo_root_path}/${hw_dir}/top.hwdef -force

if { [expr [package vcompare [clean_version] 2019.2 ] < 0] } {
    # create the 
    write_sysdef -hwdef ${apollo_root_path}/${hw_dir}/top.hwdef -bit ${apollo_root_path}/bit/top.bit -file ${apollo_root_path}/${hw_dir}/top.hdf -force
} else { 
    # create the hwdef file for old builds
    write_sysdef -hwdef ${apollo_root_path}/${hw_dir}/top.hwdef -bit ${apollo_root_path}/bit/top.bit -file ${apollo_root_path}/${hw_dir}/top -force

    #needed for next line since Xilinx is dumb
    open_checkpoint $outputDir/post_route.dcp
    #build Xilinx's new kind of filee....
    write_hw_platform -fixed -minimal -file ${apollo_root_path}/${hw_dir}/top.xsa -force
}


#create any debugging files
write_debug_probes -force ${apollo_root_path}/bit/top.ltx                                                                

if { [expr {![catch {file lstat ${apollo_root_path}/configs/${build_name}/Generate_svf.tcl finfo}]}] } {
    source  ${apollo_root_path}/configs/${build_name}/Generate_svf.tcl
}
