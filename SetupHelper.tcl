proc ProcessFileListFile {filename} {
    global apollo_root_path
    global build_name
    global buid_scripts_path
    global autogen_path
    global BD_PATH
    
    source ${filename}

    #Add vhdl files
    for {set j 0} {$j < [llength $vhdl_files ] } {incr j} {
	set filename "${apollo_root_path}/[lindex $vhdl_files $j]"
	if { [file extension ${filename} ] == ".v" } {
	    read_verilog $filename
	    puts "Adding verilog file: $filename"
	} else {
	    read_vhdl $filename
	    puts "Adding VHDL file: $filename"
	}	
    }

    #Check for syntax errors
    set syntax_check_info [check_syntax -return_string]
    #if {[string first "is not declared" ${syntax_check_info} ] > -1} {
    #    puts ${syntax_check_info}
    #    exit
    #}
    #if {[string first "Syntax error" ${syntax_check_info}] > -1 } {
    #    error ${syntax_check_info}    
    #}
    


    #Add xci files
    if { [info exists xci_files] == 1 } {
	set ip_list {}
	for {set j 0} {$j < [llength $xci_files ] } {incr j} {
	    set filename "${apollo_root_path}/[lindex $xci_files $j]"
	    set ip_name [file rootname [file tail $filename]]
	    puts "Adding $filename"    
	    if { [file extension ${filename} ] == ".tcl" } {
		source ${filename}
	    } else {
		#normal xci file
		read_ip $filename
		set isLocked [get_property IS_LOCKED [get_ips $ip_name]]
		puts "IP $ip_name : locked = $isLocked"
		set upgrade  [get_property UPGRADE_VERSIONS [get_ips $ip_name]]
		if {$isLocked && $upgrade != ""} {
		    puts "Upgrading IP"
		    upgrade_ip [get_ips $ip_name]
		}    
	    }
	    lappend ip_list [get_ips $ip_name]
	}
	puts "Generating target all on ${ip_list}"
	generate_target all [get_ips $ip_name]  
	puts "Running synth on ${ip_list}"
	synth_ip ${ip_list}
    }


    #Add bd files
    foreach bd_name [array names bd_files] {
	set filename "${apollo_root_path}/$bd_files($bd_name)"
	source $filename
	puts "Running $filename"
	read_bd [get_files "${apollo_root_path}/$bd_path/$bd_name/$bd_name.bd"]
	open_bd_design [get_files "${apollo_root_path}/$bd_path/$bd_name/$bd_name.bd"]
	if { [catch start_gui] == 0 } { 
	    puts "INFO: gui successfully opened, writing block design layout"
	    write_bd_layout -quiet -force -format svg -orientation portrait ../doc/${build_name}_${bd_name}.svg
	    stop_gui
	} else { 
	    puts "INFO: gui did not open, skip write block design layout"
	}
	make_wrapper -files [get_files $bd_name.bd] -top -import -force
	set bd_wrapper $bd_name
	append bd_wrapper "_wrapper.vhd"
	read_vhdl [get_files $bd_wrapper]       
    }


    #Add xdc files
    for {set j 0} {$j < [llength $xdc_files ] } {incr j} {
	set filename "${apollo_root_path}/[lindex $xdc_files $j]"
	read_xdc $filename
	puts "Adding $filename"
    }
}
