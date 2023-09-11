#!/usr/bin/env python3
#################################################################################                                                                                                             
## Force python3                                                                                                                                                                              
#################################################################################                                                                                                             
import sys

if not sys.version_info.major == 3:                                                                                                                                                           
    raise BaseException("Wrong Python version detected.  Please ensure that you are using Python 3.")                                                                                         
#################################################################################              

import re
import argparse
from pprint import pprint

AXIReadMOSI = {
    "name":        "AXIReadMOSI",
    "ending":      "RMOSI",
    "dir":         "out",
    "pkg_signals": {
        "ARADDR":      {"new_name": "address",         "width":"AXI_ADDR_WIDTH"},
        "ARID"  :      {"new_name": "address_ID",      "width":"AXI_ID_BIT_COUNT"},
        "ARPROT":      {"new_name": "protection_type", "width":"3"},
        "ARVALID":     {"new_name": "address_valid",   "width":"1"},
        "ARLEN":       {"new_name": "burst_length",    "width":"8"},
        "ARSIZE":      {"new_name": "burst_size",      "width":"3"},
        "ARBURST":     {"new_name": "burst_type",      "width":"2"},
        "ARLOCK":      {"new_name": "lock_type",       "width":"1"},
        "ARCACHE":     {"new_name": "cache_type",      "width":"4"},
        "ARQOS":       {"new_name": "qos",             "width":"4"},
        "ARREGION":    {"new_name": "region",          "width":"4"},
        "ARUSER":      {"new_name": "address_user",    "width":"4"},
        "RREADY":      {"new_name": "ready_for_data",  "width":"1"}
    }
}

AXIReadMISO = {
    "name":        "AXIReadMISO",
    "ending":      "RMISO",
    "dir":         "in",
    "pkg_signals": {
        "ARREADY":     {"new_name": "ready_for_address",  "width":"1"},
        "RID":         {"new_name": "data_ID",  "width":"AXI_ID_BIT_COUNT"},
        "RDATA":       {"new_name": "data",  "width":"32"},
        "RVALID":      {"new_name": "data_valid",  "width":"1"},
        "RRESP":       {"new_name": "response",  "width":"2"},
        "RLAST":       {"new_name": "last",  "width":"1"},
        "RUSER":       {"new_name": "data_user",  "width":"4"}
    }    
}

AXIWriteMOSI = {
    "name":        "AXIWriteMOSI",
    "ending":      "WMOSI",
    "dir":         "out",
    "pkg_signals": {
        "AWADDR":    {"new_name": "address",  "width":"AXI_ADDR_WIDTH"},
        "AWID":      {"new_name": "address_ID",  "width":"AXI_ID_BIT_COUNT"},
        "AWPROT":    {"new_name": "protection_type",  "width":"3"},
        "AWVALID":   {"new_name": "address_valid",  "width":"1"},
        "AWLEN":     {"new_name": "burst_length",  "width":"8"},
        "AWSIZE":    {"new_name": "burst_size",  "width":"3"},
        "AWBURST":   {"new_name": "burst_type",  "width":"2"},
        "AWLOCK":    {"new_name": "lock_type",  "width":"1"},
        "AWCACHE":   {"new_name": "cache_type",  "width":"4"},
        "AWQOS":     {"new_name": "qos",  "width":"4"},
        "AWREGION":  {"new_name": "region",  "width":"4"},
        "AWUSER":    {"new_name": "address_user",  "width":"4"},
        "WID":       {"new_name": "write_ID",  "width":"AXI_ID_BIT_COUNT"},
        "WDATA":     {"new_name": "data",  "width":"32"},
        "WVALID":    {"new_name": "data_valid",  "width":"1"},
        "WSTRB":     {"new_name": "data_write_strobe",  "width":"4"},
        "WLAST":     {"new_name": "last",  "width":"1"},
        "WUSER":     {"new_name": "data_user",  "width":"4"},
        "BREADY":    {"new_name": "ready_for_response",  "width":"1"}
    }
}

AXIWriteMISO = {
    "name":        "AXIWriteMISO",
    "ending":      "WMISO",
    "dir":         "in",
    "pkg_signals": {
        "AWREADY":   {"new_name": "ready_for_address",  "width":"1"},
        "WREADY":    {"new_name": "ready_for_data",  "width":"1"},
        "BID":       {"new_name": "response_ID",  "width":"AXI_ID_BIT_COUNT"},
        "BVALID":    {"new_name": "response_valid",  "width":"1"},
        "BRESP":     {"new_name": "response",  "width":"2"},
        "BUSER":     {"new_name": "response_user",  "width":"4"}
    }
}

AXIReadMOSI_d64 = {
    "name":        "AXIReadMOSI_d64",
    "ending":      "RMOSI",
    "dir":         "out",
    "pkg_signals": {
        "ARADDR":      {"new_name": "address",         "width":"AXI_ADDR_WIDTH"},
        "ARID"  :      {"new_name": "address_ID",      "width":"AXI_ID_BIT_COUNT"},
        "ARPROT":      {"new_name": "protection_type", "width":"3"},
        "ARVALID":     {"new_name": "address_valid",   "width":"1"},
        "ARLEN":       {"new_name": "burst_length",    "width":"8"},
        "ARSIZE":      {"new_name": "burst_size",      "width":"3"},
        "ARBURST":     {"new_name": "burst_type",      "width":"2"},
        "ARLOCK":      {"new_name": "lock_type",       "width":"1"},
        "ARCACHE":     {"new_name": "cache_type",      "width":"4"},
        "ARQOS":       {"new_name": "qos",             "width":"4"},
        "ARREGION":    {"new_name": "region",          "width":"4"},
        "ARUSER":      {"new_name": "address_user",    "width":"4"},
        "RREADY":      {"new_name": "ready_for_data",  "width":"1"}
    }
}

AXIReadMISO_d64 = {
    "name":        "AXIReadMISO_d64",
    "ending":      "RMISO",
    "dir":         "in",
    "pkg_signals": {
        "ARREADY":     {"new_name": "ready_for_address",  "width":"1"},
        "RID":         {"new_name": "data_ID",  "width":"AXI_ID_BIT_COUNT"},
        "RDATA":       {"new_name": "data",  "width":"64"},
        "RVALID":      {"new_name": "data_valid",  "width":"1"},
        "RRESP":       {"new_name": "response",  "width":"2"},
        "RLAST":       {"new_name": "last",  "width":"1"},
        "RUSER":       {"new_name": "data_user",  "width":"4"}
    }    
}

AXIWriteMOSI_d64 = {
    "name":        "AXIWriteMOSI_d64",
    "ending":      "WMOSI",
    "dir":         "out",
    "pkg_signals": {
        "AWADDR":    {"new_name": "address",  "width":"AXI_ADDR_WIDTH"},
        "AWID":      {"new_name": "address_ID",  "width":"AXI_ID_BIT_COUNT"},
        "AWPROT":    {"new_name": "protection_type",  "width":"3"},
        "AWVALID":   {"new_name": "address_valid",  "width":"1"},
        "AWLEN":     {"new_name": "burst_length",  "width":"8"},
        "AWSIZE":    {"new_name": "burst_size",  "width":"3"},
        "AWBURST":   {"new_name": "burst_type",  "width":"2"},
        "AWLOCK":    {"new_name": "lock_type",  "width":"1"},
        "AWCACHE":   {"new_name": "cache_type",  "width":"4"},
        "AWQOS":     {"new_name": "qos",  "width":"4"},
        "AWREGION":  {"new_name": "region",  "width":"4"},
        "AWUSER":    {"new_name": "address_user",  "width":"4"},
        "WID":       {"new_name": "write_ID",  "width":"AXI_ID_BIT_COUNT"},
        "WDATA":     {"new_name": "data",  "width":"64"},
        "WVALID":    {"new_name": "data_valid",  "width":"1"},
        "WSTRB":     {"new_name": "data_write_strobe",  "width":"4"},
        "WLAST":     {"new_name": "last",  "width":"1"},
        "WUSER":     {"new_name": "data_user",  "width":"4"},
        "BREADY":    {"new_name": "ready_for_response",  "width":"1"}
    }
}

AXIWriteMISO_d64 = {
    "name":        "AXIWriteMISO_d64",
    "ending":      "WMISO",
    "dir":         "in",
    "pkg_signals": {
        "AWREADY":   {"new_name": "ready_for_address",  "width":"1"},
        "WREADY":    {"new_name": "ready_for_data",  "width":"1"},
        "BID":       {"new_name": "response_ID",  "width":"AXI_ID_BIT_COUNT"},
        "BVALID":    {"new_name": "response_valid",  "width":"1"},
        "BRESP":     {"new_name": "response",  "width":"2"},
        "BUSER":     {"new_name": "response_user",  "width":"4"}
    }
}





AXITypes = {
    "AXIReadMOSI": AXIReadMOSI,
    "AXIReadMISO": AXIReadMISO,
    "AXIWriteMOSI": AXIWriteMOSI,
    "AXIWriteMISO": AXIWriteMISO,    
    "AXIReadMOSI_d64": AXIReadMOSI_d64,
    "AXIReadMISO_d64": AXIReadMISO_d64,
    "AXIWriteMOSI_d64": AXIWriteMOSI_d64,
    "AXIWriteMISO_d64": AXIWriteMISO_d64,    

}


def SwitchDir(value):
    if value.upper() == "OUT":
        return "in"
    return "out"

def GeneratePortInterface(port_list):
    name_replacements = dict()

    axi_endpoint_signals= dict()
    axi_master_signals=dict()
    other_signals = ""
    
    for line in port_list:
        found=False
        for pkg_type in (AXIReadMOSI,AXIReadMISO,AXIWriteMOSI,AXIWriteMISO):
            #loop over possible axi record type for this signal
            for signal , signal_info in pkg_type["pkg_signals"].items():

                package_to_use = pkg_type
                
                #search for this signal in this line
#                regex_string=r"^ *(.*)_(" + re.escape(signal) + r") *: *(in|out) *(.*);"
                regex_string=r"^ *(.*)_(" + re.escape(signal) + r") *: *(in|out) *(.*)"
                matches=re.findall(regex_string,line,re.IGNORECASE)
                if len(matches) == 0:
                    continue
                elif len(matches[0]) < 4 :
                    raise Exception("AXI signal regex match contains the wrong number of submatches"+line)                
                #match found
                axi_name=matches[0][0].upper()
                signal_name=matches[0][1].upper()
                signal_dir=matches[0][2].upper()
                signal_type=matches[0][3].upper()
                signal_width=1
                #find width of type
                regex_string=r"std_logic_vector\s*\(\s*([0-9]+)\s*[a-z]*\s*([0-9]+)\s*\)"
                matches=re.findall(regex_string,signal_type,re.IGNORECASE)
                if len(matches) > 0:
                    if len(matches[0]) > 1:
                        signal_width = abs(int(matches[0][0]) - int(matches[0][1]))+1
                        
                #CHeck if this is the 32 or 64 bit version of this record
                pkg_type_to_use=pkg_type["name"]
                if signal_width > 32:
                    pkg_type_to_use=pkg_type["name"]+"_d64"


                #check if this is a master or endpoint interface
                if signal_dir.upper() == pkg_type["dir"].upper():
                    #axi endpoint
                    #replacement look up
                    name_replacements[axi_name+"_"+signal_name] = {"axi_name": axi_name,"ending": pkg_type["ending"], "pkg_signal": pkg_type["pkg_signals"][signal.upper()]}
                    #signals to add to the file
                    if axi_name in axi_endpoint_signals.keys():
                        axi_endpoint_signals[axi_name][pkg_type_to_use] = pkg_type_to_use
                    else:
                        axi_endpoint_signals[axi_name] = {pkg_type_to_use: pkg_type_to_use}
                else:
                    #axi master
                    #replacement look up
                    name_replacements[axi_name+"_"+signal_name] = {"axi_name": axi_name,"ending": pkg_type["ending"], "pkg_signal": pkg_type["pkg_signals"][signal.upper()]}
                    #name_replacements[axi_name+"_"+signal_name] = axi_name+"_"+pkg_type["ending"]+"."+pkg_type["pkg_signals"][signal.upper()]
                    #signals to add to the file
                    if axi_name in axi_master_signals.keys():
                        axi_master_signals[axi_name][pkg_type_to_use] = pkg_type_to_use
                    else:
                        axi_master_signals[axi_name] = {pkg_type_to_use: pkg_type_to_use}
                found = True
                break
            if found:
                break
        if not found:
            other_signals= other_signals + line

    #Clean up any 32/64 bit issues
    for endpoint,sub_types in axi_endpoint_signals.items():
        d64_entries=[]
        for key,sub_type in sub_types.items():
            d64_found_position=key.find("_d64")
            if  d64_found_position > 0:                
                d64_entries.append(key[:d64_found_position])

        #we have a mix of d64 entries, we need to convert to all d64
        if len(d64_entries) > 0:
            #remove non64 versions of 64 entries
            for entry_name in d64_entries:
                sub_types.pop(entry_name)
            #move other records to their 64 versions
            for key,sub_type in list(sub_types.items()):
                if key.find("_d64") == -1:
                    #TODO, does the second value in this ever get used? It isn't changed here
                    sub_types[key+"_d64"] = sub_types[key]
                    sub_types.pop(key)


                    
    #Generate the new port map
    output_data = ""
    #process AXI connections (masters)
    for master,sub_types in axi_master_signals.items():
        output_data= output_data + "    --AXI master--\n"
        for key,sub_type in sub_types.items():
            output_data= output_data + "    %-15s : % 3s %s;\n" % (
                master+"_"+AXITypes[key]["ending"],
                SwitchDir(AXITypes[key]["dir"]),
                key
            )
    #process AXI connections (endpoints)
    for endpoint,sub_types in axi_endpoint_signals.items():
        output_data= output_data + "    --AXI endpoint--\n"
        for key,sub_type in sub_types.items():
            output_data= output_data + "    %-15s : % 3s %s;\n" % (
                endpoint+"_"+AXITypes[key]["ending"],
                AXITypes[key]["dir"],
                key
            )
    output_data= output_data + "\n"
    for signal in other_signals:
        output_data=output_data + signal
    return (output_data,name_replacements)

def ProcessVHDL(data):
    new_file = "--This is an autogenerated file built from an autogenerated file.  DO NOT MODIFY\n"
    new_file = new_file + "--  Look at update_bd_wrapper.py for details\n"
    new_file = new_file + "use work.types.all;\n"
    new_file = new_file + "use work.AXIRegPKG.all;\n"
    new_file = new_file + "use work.AXIRegPKG_d64.all;\n"

    new_entity_base_name=""
    old_entity_base_name=""
    
    port_list = []
    
    #find all the endpoint names and build a map of name to the signals in the 4 records.
    state="find_interface"
    sucessful=False
    for line in data:
        #========================================================================
        if state == "find_interface":
            #Find the start of the wrappers interface
            matches = re.findall(r"^ *entity *([a-zA-Z0-9_]*) *is.*",line,re.IGNORECASE)
            if len(matches) > 0:
                #find the name of the entity we are wrapping
                entity_matches = re.findall(r"^ *entity (.*)_wrapper",line)
                if len(entity_matches) == 0:
                    raise Exception("No matches found in wrapper search: "+line)
                if len(entity_matches[0]) == 0:
                    raise Exception("No sub-matches found in wrapper search: "+line)
                old_entity_base_name=entity_matches[0]
                new_entity_base_name=old_entity_base_name+"_sane"
                line=line.replace(old_entity_base_name,new_entity_base_name)
            if line.lower().find("port") >= 0:
                #we found the beginning of the port list
                state="process_interface"
            new_file=new_file+line
        #========================================================================
        elif state == "process_interface":
            if line.find(':') >= 0:
                port_list.append(line)
            else:
                #we are at the end of the port list
                (interface_lines,signal_rename_list) = GeneratePortInterface(port_list)
                new_file=new_file+interface_lines
                #end
                state = "end_interface"
                #add this line
                new_file=new_file+line
        #========================================================================
        elif state == "end_interface":
            #find the end of the entity interface
            matches = re.findall(r"^ *end *" + re.escape(old_entity_base_name) + r"_wrapper *;.*" ,line,re.IGNORECASE)
            if len(matches) > 0:
                #update end to new name
                new_file=new_file+"end "+new_entity_base_name+"_wrapper;\n"
                state="find_architecture"
            else:
                #copy old line
                new_file=new_file+line                
        #========================================================================
        elif state == "find_architecture":
            #find the architecture line and update the name
            matches = re.findall(r"^ *architecture *([a-zA-Z]*) *of *" + re.escape(old_entity_base_name) + r"_wrapper *is.*",line,re.IGNORECASE)
            if len(matches) > 0:
                #update end to new name
                new_file=new_file+"architecture "+matches[0]+" of "+new_entity_base_name+"_wrapper is\n"
                state="find_component"
            else:
                #copy old line
                new_file=new_file+line                
        #========================================================================
        elif state == "find_component":
            new_file=new_file+line
            matches = re.findall(r"^ *component *" + re.escape(old_entity_base_name) + r" *is.*",line,re.IGNORECASE)
            if len(matches) > 0:
                #found the beginning of the main component (but not the port word). 
                state="find_component_port"
        #========================================================================
        elif state == "find_component_port":
            new_file=new_file+line
            matches = re.findall(r"^ *port *\( *(.*)",line,re.IGNORECASE)
            if len(matches) > 0 :
                if len(matches[0]) > 0:
                    raise Exception("port line has text after the opening (: "+line)
                state="update_component"
        #========================================================================
        elif state == "update_component":
            
            matches = re.findall(r"^ *\) *; *",line,re.IGNORECASE)
            if len(matches) > 0:
                new_file=new_file+line
                state = "find_instance"                
                continue
            if line.count('(') - line.count(')') != 0:
                raise Exception("component declaration has non-ending line with unbalanced parentheses.  I'm not dealing with that!: "+line)
#            dec_match = re.findall(r"^ *([a-zA-Z0-9_]*) *: *(inout|out|in) *(.*) *; *",line)
            dec_match = re.findall(r"^ *([a-zA-Z0-9_]*) *: *(inout|out|in) *(.*) *",line)
            if len(dec_match) > 0:
                #we have a match to a port description
                for name in signal_rename_list.keys():
                    #search through our update list to find this register for naming issues
                    update_match = re.findall(r"^"+re.escape(name)+r" *$",dec_match[0][0],re.IGNORECASE)                    
                    if len(update_match) > 0:
                        if signal_rename_list[name]["pkg_signal"]["width"] == "1":
                            #this register has a width of 1 and vivado might mess this up, fix the name
                            if len(re.findall(r"\( *[0-9]* *(downto|to) *[0-9]* *\)",dec_match[0][2],re.IGNORECASE)) > 0:
                                signal_rename_list[name]["source_ending"] = "(0)"
                                break

                                
#                new_file=new_file +"    %-40s : %-5s %s;\n" % ( dec_match[0][0], dec_match[0][1], dec_match[0][2] )
                new_file=new_file +"    %-40s : %-5s %s\n" % ( dec_match[0][0], dec_match[0][1], dec_match[0][2] )
            else:
                new_file=new_file+line
        #========================================================================
        elif state == "find_instance":
            new_file=new_file+line
            matches = re.findall(r"^ *"+re.escape(old_entity_base_name)+r".* *: *component *"+re.escape(old_entity_base_name),line,re.IGNORECASE)
            if len(matches) > 0 :
                #found the start of this instance
                state= "find_instance_port"
        #========================================================================
        elif state == "find_instance_port":
            new_file=new_file+line
            matches = re.findall(r"^ *port *map *\( *(.*)?",line,re.IGNORECASE)
            if len(matches) > 0 :
                if len(matches[0]) > 0:
                    raise Exception("port line has text after the opening (: "+line)
                state="update_instance"
        #========================================================================
        elif state == "update_instance":
            #look for the end of this instance ");"
            matches = re.findall(r"^ *\) *; *",line,re.IGNORECASE)
            if len(matches) > 0:
                new_file=new_file+line
                state = "finish_up"
                continue
            if line.count('(') - line.count(')') != 0:
                raise Exception("instance declaration has non-ending line with unbalanced parentheses.  I'm not dealing with that!: "+line)
            dec_match = re.findall(r"^ *([a-zA-Z0-9_]*)(.*)=> *([a-zA-Z0-9_]*)([\(\)0-9downt ]*)(,)?",line,re.IGNORECASE)
            if len(dec_match) > 0:
                source_ending=""
                #we have a match to a port description
                updated_name=""
                found=False
                for name in signal_rename_list.keys():
                    #search through our update list to find this register for naming issues
                    update_match = re.findall(r"^"+re.escape(name),dec_match[0][2],re.IGNORECASE)                    
                    if len(update_match) > 0:
                        pkg_signal = signal_rename_list[name]["pkg_signal"]
                        updated_name= signal_rename_list[name]["axi_name"]+"_"+signal_rename_list[name]["ending"]+"."+pkg_signal["new_name"]
                        
                        if "source_ending" in signal_rename_list[name].keys():
                            source_ending=signal_rename_list[name]["source_ending"]
                        found=True
                        break
                if not found:
                    updated_name=dec_match[0][2]
                ending=""
                if len(dec_match[0]) == 5:
                    ending=dec_match[0][4]
                new_file=new_file +"    %-40s => %s%s\n" % ( dec_match[0][0]+source_ending, updated_name, ending)
                
            else:
                new_file=new_file+line
        #========================================================================
        else: #if state == "finish_up":
            new_file=new_file+line
            
    return new_file


def ProcessWrapper(inFile,outFile):
    #open file
    try:
        with open(inFile,'r') as wrapper_file:
            #read file contents
            wrapper_contents=wrapper_file.readlines()        
            #process file (rewrite bd wrapper)
            new_contents=ProcessVHDL(wrapper_contents)
    except IOError as ioe:
        print("Error opening ",inFile," ",ioe)
        
    try:
        with open(outFile,'w') as output_file:
            output_file.write(new_contents)
    except IOError as ioe:
        print("Error opening ",outFile," ",ioe)
        
        
if __name__ == "__main__":
    #command line
    parser = argparse.ArgumentParser(description="Clean-up bd wrappepr vhdl file")
    parser.add_argument("--source_file","-i"      ,help="input bd wrapper vhdl filename",required=True)
    parser.add_argument("--dest_file","-o"      ,help="output sane bd wrapper vhdl filename",required=True)
    args=parser.parse_args()
    ProcessWrapper(inFile=args.source_file,outFile=args.dest_file)

