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
import numbers

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
    print("Generate HDL for "+name+" from "+XMLFile)
    
    #get working directory
#    wd=os.getcwd()
    print(HDLPath)
    print(XMLFile)
    print(map_template_file)
    build_vhdl_packages.build_vhdl_packages(useSimpleParser,
                                            False,
                                            False,
                                            map_template_file,                                            #os.path.abspath(map_template_file),
                                            None,
                                            HDLPath, #                                            os.path.abspath(wd+"/"+HDLPath),
                                            XMLFile, #                                            os.path.abspath(wd+"/"+XMLFile),
                                            name)
    




#================================================================================
#process a single slave (or tree us sub-slaves) and update all the output files
#================================================================================
def LoadSlave(name,slave,aTableYAML,parentName,map_template_file,pkg_template_file,useSimpleParser,autogen_path,root_path,build_name):
    
    fullName=str(name)
    
    print("Processing "+fullName)

    #Build HDL for this file
    if 'INCLUDE_FILE' in slave:
        wd=os.getcwd()
        configFileName = slave['INCLUDE_FILE']
        configFileName = configFileName.replace("${::apollo_root_path}",root_path)
        configFileName = configFileName.replace("${::build_name}",build_name)

        print(os.getcwd())
        os.chdir(os.path.dirname(configFileName))
        print(os.getcwd())
        
        LoadYAMLFile(
            configFileName,
            aTableYAML,
            map_template_file,
            pkg_template_file,
            useSimpleParser,
            autogen_path,
            root_path,
            build_name)
        os.chdir(wd)
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
            map_template_file = root_path+"/regmap_helper/templates/"+slave['HDL']['map_template']
            print("  Using map template file: "+map_template_file)
        if 'pkg_template' in slave['HDL']:
            pkg_template_file = root_path+"/regmap_helper/templates/"+slave['HDL']['pkg_template']

        GenerateHDL(fullName,
                    slave['XML'],
                    out_dir,
                    map_template_file,
                    pkg_template_file,
                    useSimpleParser)
    
    #generate yaml for the kernel and centos build
    if 'UHAL_BASE' in slave:
        if 'XML' in slave:
            #test if file exists
            xmlFileName = slave['XML'].replace("${::apollo_root_path}",root_path)
            xmlFileName = xmlFileName.replace("${::build_name}",build_name)
            print(xmlFileName)
            if xmlFileName[0] != '/':
                xmlFileName= os.path.abspath(xmlFileName)            
            #update the address table file
            if isinstance(slave['UHAL_BASE'],numbers.Number):
                slave['UHAL_BASE'] = "0x"+hex(slave['UHAL_BASE'])[2:].zfill(8)
                
            aTableYAML[name]={
                "UHAL_BASE": slave['UHAL_BASE'],
                "XML": xmlFileName}

      
        else:
            raise RuntimeError(fullName+" has UHAL_BASE tag, but no XML tag\n")

    #Handle and additional slaves generated by the TCL command
    if 'SUB_SLAVES' in slave:
        if slave['SUB_SLAVES'] != None:
            for subSlave in slave['SUB_SLAVES']:
                LoadSlave(subSlave,
                          slave['SUB_SLAVES'][subSlave],
                          aTableYAML,
                          fullName,
                          map_template_file,
                          pkg_template_file,
                          useSimpleParser,
                          autogen_path,
                          root_path,
                          build_name
                         )




def LoadYAMLFile(configFileName,aTableYAML,map_template_file,pkg_template_file,useSimpleParser,autogen_path,root_path,build_name):
    #source slave yaml to drive the rest of the build
    configFile=open(configFileName)
    config=yaml.safe_load(configFile)
    for slave in config['AXI_SLAVES']:
        #update all the files for this slave
        LoadSlave(slave,
                  config["AXI_SLAVES"][slave],
                  aTableYAML,
                  "",
                  map_template_file,
                  pkg_template_file,                        
                  useSimpleParser,
                  autogen_path,
                  root_path,
                  build_name
        )

    
                
def main(addressTablePath,addressTableFile, configFileName,map_template_file,pkg_template_file,autogen_path,useSimpleParser,root_path,build_name):
    # configure logger
    global log

    

    #address table yaml file
    addressTableYAMLFile=open(addressTablePath+"/"+addressTableFile,"w")
    aTableYAML = dict()

    LoadYAMLFile(configFileName,aTableYAML,map_template_file,pkg_template_file,useSimpleParser,autogen_path,root_path,build_name)
    
    aTableYAML={"UHAL_MODULES": aTableYAML}
  
    addressTableYAMLFile.write(yaml.dump(aTableYAML,
                                         Dumper=MyDumper,
                                         default_flow_style=False))


if __name__ == "__main__":
    #command line
    parser = argparse.ArgumentParser(description="Create auto-generated files for the build system.")
    parser.add_argument("--configFile","-s"      ,help="YAML file storing the slave info for generation",required=True)
    parser.add_argument("--addressTablePath","-a",help="Path for address table generation yaml",required=True)
    parser.add_argument("--addressTableFile","-f",help="filename for address table generation yaml",required=False,default="config.yaml")
    parser.add_argument("--mapTemplate","-m"        ,help="Path for map_template file",required=False)
    parser.add_argument("--pkgTemplate","-p"        ,help="Path for pkg_template file",required=False)
    parser.add_argument("--autogenPath","-g"        ,help="Base path for autogenerated files",required=True)
    parser.add_argument("--useSimpleParser","-u"        ,type=str2bool,help="Use simple parser",required=False,default=True)
    parser.add_argument("--root_path","-r"          ,help="Root path for build",required=False,default="./")
    parser.add_argument("--build_name","-b"         ,help="Build name",required=True)
    args=parser.parse_args()
    main(
        addressTablePath  = args.addressTablePath, 
        addressTableFile  = args.addressTableFile, 
        configFileName    = args.configFile,
        map_template_file = args.mapTemplate,
        pkg_template_file = args.pkgTemplate,
        autogen_path      = (os.getcwd()+'/'+args.autogenPath),
        useSimpleParser   = args.useSimpleParser,
        root_path         = args.root_path,
        build_name        = args.build_name
        
    )
