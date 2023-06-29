proc ProcessFileListFile {filename recursive_includes} {
    global apollo_root_path
    global build_name
    global buid_scripts_path
    global autogen_path
    global BD_PATH
    global C2C
    global C2CB

    
    puts "============================================================="
    puts "Processing file list $filename"
    for {set j [expr [llength $recursive_includes] -1] } {$j >= 0  } {incr j -1} {
	puts "included from [lindex $recursive_includes] $j]"
    }    
    if { [llength $recursive_includes] > 30 } {
	error "Error, recursion limit reached"	
    }
    
    puts "============================================================="


    
    source ${filename}

    #Add vhdl files
    if { [info exists vhdl_files] == 1 } {
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
    if { [info exists bd_files] == 1 } {
	foreach bd_name [array names bd_files] {
	    set filename "${apollo_root_path}/$bd_files($bd_name)"
	    puts "Running $filename"
	    source $filename
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
	    set wrapper_file [make_wrapper -files [get_files $bd_name.bd] -top -force]
	    set wrapper_file_sane [string map {_wrapper.vhd _sane_wrapper.vhd} $wrapper_file]
	    puts "Modifying ${bd_name} wrapper file ${wrapper_file}"
	    set output_text [exec ../build-scripts/update_bd_wrapper.py -i $wrapper_file -o $wrapper_file_sane]
	    puts "Adding ${wrapper_file_sane}"
	    read_vhdl $wrapper_file_sane
	    #?
	    set_property synth_checkpoint_mode None [get_files $bd_name.bd]
	}
    }

    #Add xdc files
    if { [info exists xdc_files] == 1 } {
	for {set j 0} {$j < [llength $xdc_files ] } {incr j} {
	    set filename "${apollo_root_path}/[lindex $xdc_files $j]"
	    read_xdc $filename
	    puts "Adding $filename"
	}	
    }

    #include files
    if { [info exists include_files] == 1 } {
	#setup recursion 
	set next_list $recursive_includes	    
	lappend next_list $filename

	for {set j 0} {$j < [llength $include_files ] } {incr j} {
	    set next_included_file "${apollo_root_path}/[lindex $include_files $j]"	    
	    ProcessFileListFile $next_included_file $next_list 
	}
    }
}
