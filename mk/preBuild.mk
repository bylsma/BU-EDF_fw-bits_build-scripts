#CACTUS_ROOT:="/opt/cactus"
#CACTUS_LD_PATH:=$(CACTUS_ROOT)"/lib/"

#################################################################################
# Clean
#################################################################################
clean_prebuild:
	@echo "Cleaning up prebuild autogenerated files"
	@rm -f $(ADDSLAVE_TCL_PATH)/AddSlaves*.tcl 
	@rm -f $(ADDRESS_TABLE_CREATION_PATH)/slaves*.yaml
	@rm -rf $(ADDRESS_TABLE_CREATION_PATH)/address_table/*
	@rm -f $(SLAVE_DTSI_PATH)/slaves*.yaml

#################################################################################
# generate prebuilds for FPGA builds in config
#################################################################################
define PREBUILD_template =
 prebuild_$(1):  $(SLAVE_DTSI_PATH)/slaves_$(1).yaml $(ADDRESS_TABLE_CREATION_PATH)/slaves_$(1).yaml $(ADDSLAVE_TCL_PATH)/AddSlaves.tcl
endef
PREBUILDS=$(addprefix,prebuild_,$(CONFIGS))


#################################################################################
# prebuild 
#################################################################################
ifdef CACTUS_ROOT
       USE_SIMPLE_PARSER=-u False
       CACTUS_LD_PATH:=$(CACTUS_ROOT)"/lib/"
else
       USE_SIMPLE_PARSER=-u True
endif


$(SLAVE_DTSI_PATH)/slaves_%.yaml $(ADDRESS_TABLE_CREATION_PATH)/slaves_%.yaml : $(SLAVE_DEF_FILE_BASE)/%/slaves.yaml
	@mkdir -p $(ADDRESS_TABLE_CREATION_PATH)
	@mkdir -p $(SLAVE_DTSI_PATH)
	@mkdir -p $(SLAVE_DEF_FILE_BASE)/$*/autogen
	LD_LIBRARY_PATH=$(CACTUS_LD_PATH) ./build-scripts/preBuild.py \
			                     -s $^ \
				             -t $(ADDSLAVE_TCL_PATH) \
				             -a $(ADDRESS_TABLE_CREATION_PATH) \
                                             -f slaves_$*.yaml \
				             -d $(SLAVE_DTSI_PATH) \
                                             -m $(MAP_TEMPLATE_FILE) \
                                             $(USE_SIMPLE_PARSER) \
                                             -g $(CONFIGS_BASE_PATH)/$*/autogen
	make address_table

$(foreach prebuild,$(CONFIGS),$(eval $(call PREBUILD_template,$(prebuild))))

