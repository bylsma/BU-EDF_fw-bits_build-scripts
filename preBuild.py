#!/usr/bin/env python3
#################################################################################                                                                                                             
## Force python3                                                                                                                                                                              
#################################################################################                                                                                                             
import sys                                                                                                                                                                                    
if not sys.version_info.major == 3:                                                                                                                                                           
    raise BaseException("Wrong Python version detected.  Please ensure that you are using Python 3.")                                                                                         
#################################################################################              

import argparse
import sys
import os
import yaml
sys.path.append("./regmap_helper")
import build_vhdl_packages

def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '')

yaml.add_representer(type(None), represent_none)

class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')



#================================================================================
#Generate the MAP and PKG VHDL files for this slave
#================================================================================
def GenerateHDL(name,XMLFile,HDLPath,map_template_file,pkg_template_file,useSimpleParser):
    print("Generate HDL for"+name+"from"+XMLFile)
    
    #get working directory
    wd=os.getcwd()

    build_vhdl_packages.build_vhdl_packages(useSimpleParser,
                                            False,
                                            False,
                                            os.path.abspath(map_template_file),
                                            None,
                                            os.path.abspath(wd+"/"+HDLPath),
                                            os.path.abspath(wd+"/"+XMLFile),
                                            name)
    




#================================================================================
#process a single slave (or tree us sub-slaves) and update all the output files
#================================================================================
def LoadSlave(name,slave,dtsiYAML,aTableYAML,parentName,map_template_file,pkg_template_file,useSimpleParser,autogen_path="./"):
    
    fullName=str(name)
    
    print("Processing "+fullName)

    #Build HDL for this file
    if 'HDL' in slave:
        if 'XML' not in slave:
            raise RuntimeError(fullName+" has HDL tag, but no XML tag\n")

        if 'out_dir' not in slave['HDL']:
            if 'out_name' not in slave['HDL']:
                out_dir = autogen_path+"/"+name+"/"
            else:
                out_dir = autogen_path+"/"+slave['HDL']['out_name']+"/"
                fullName=slave['HDL']['out_name']
            print("  Using (autogen path) "+out_dir+" for HDL generation")
        else:
            out_dir = slave['HDL']['out_dir']
            print("  Using "+out_dir+" for HDL generation")
            if 'out_name' in slave['HDL']:
                print("  Warning, out_dir and out_name specified.  Ignoring out_name")

        if 'map_template' in slave['HDL']:
            map_template_file = "regmap_helper/templates/"+slave['HDL']['map_template']
            print("  Using map template file: "+map_template_file)
        if 'pkg_template' in slave['HDL']:
            pkg_template_file = "regmap_helper/templates/"+slave['HDL']['pkg_template']

        GenerateHDL(fullName,slave['XML'][0],out_dir,map_template_file,pkg_template_file,useSimpleParser)
    
    #generate yaml for the kernel and centos build
    if 'UHAL_BASE' in slave:
        if 'XML' in slave:
            #update list dtsi files to look for (.dtsi_chunk or .dtsi_post_chunk)
            dtsiYAML[name]=None
            #update the address table file          
#            aTableYAML[fullName]={
            aTableYAML[name]={
                "UHAL_BASE":"0x"+hex(slave['UHAL_BASE'])[2:].zfill(8),
                "XML":slave['XML']}
      
        else:
            raise RuntimeError(fullName+" has UHAL_BASE tag, but no XML tag\n")

    #Handle and additional slaves generated by the TCL command
    if 'SUB_SLAVES' in slave:
        if slave['SUB_SLAVES'] != None:
            for subSlave in slave['SUB_SLAVES']:
                LoadSlave(subSlave,
                          slave['SUB_SLAVES'][subSlave],
                          dtsiYAML,
                          aTableYAML,
                          fullName,
                          map_template_file,
                          pkg_template_file,
                          useSimpleParser,
                          autogen_path
                         )





def main(addSlaveTCLPath, dtsiPath, addressTablePath,addressTableFile, configFileName,map_template_file,pkg_template_file,autogen_path,useSimpleParser):
    # configure logger
    global log

    
    #dtsi yaml file
    dtsiYAMLFile=open(dtsiPath+"/"+addressTableFile,"w")
    dtsiYAML = dict()

    #address table yaml file
    addressTableYAMLFile=open(addressTablePath+"/"+addressTableFile,"w")
    aTableYAML = dict()

    #source slave yaml to drive the rest of the build
    configFile=open(configFileName)
    config=yaml.load(configFile)
    for slave in config['AXI_SLAVES']:
        #update all the files for this slave
        LoadSlave(slave,
                  config["AXI_SLAVES"][slave],
                  dtsiYAML,
                  aTableYAML,
                  "",
                  map_template_file,
                  pkg_template_file,                        
                  useSimpleParser,
                  autogen_path
        )

    dtsiYAML={"DTSI_CHUNKS": dtsiYAML}
    aTableYAML={"UHAL_MODULES": aTableYAML}
  
    dtsiYAMLFile.write(yaml.dump(dtsiYAML,
                                 Dumper=MyDumper,
                                 default_flow_style=False))
    addressTableYAMLFile.write(yaml.dump(aTableYAML,
                                         Dumper=MyDumper,
                                         default_flow_style=False))


if __name__ == "__main__":
    #command line
    parser = argparse.ArgumentParser(description="Create auto-generated files for the build system.")
    parser.add_argument("--configFile","-s"      ,help="YAML file storing the slave info for generation",required=True)
    parser.add_argument("--addSlaveTCLPath","-t" ,help="Path for AddConfig.tcl",required=True)
    parser.add_argument("--addressTablePath","-a",help="Path for address table generation yaml",required=True)
    parser.add_argument("--addressTableFile","-f",help="filename for address table generation yaml",required=False,default="config.yaml")
    parser.add_argument("--dtsiPath","-d"        ,help="Path for dtsi yaml",required=True)
    parser.add_argument("--mapTemplate","-m"        ,help="Path for map_template file",required=False)
    parser.add_argument("--pkgTemplate","-p"        ,help="Path for pkg_template file",required=False)
    parser.add_argument("--autogenPath","-g"        ,help="Base path for autogenerated files",required=True)
    parser.add_argument("--useSimpleParser","-u"        ,type=str2bool,help="Use simple parser",required=False,default=True)
    args=parser.parse_args()
    main(addSlaveTCLPath   = args.addSlaveTCLPath, 
         dtsiPath          = args.dtsiPath, 
         addressTablePath  = args.addressTablePath, 
         addressTableFile  = args.addressTableFile, 
         configFileName    = args.configFile,
         map_template_file = args.mapTemplate,
         pkg_template_file = args.pkgTemplate,
         autogen_path      = args.autogenPath,
         useSimpleParser   = args.useSimpleParser
    )
