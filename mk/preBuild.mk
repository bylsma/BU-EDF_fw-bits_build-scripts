#################################################################################
# Clean
#################################################################################
clean_prebuild:
	@echo "Cleaning up prebuild autogenerated files"
	@rm -f $(ADDRESS_TABLE_CREATION_PATH)config*.yaml
	@rm -rf $(ADDRESS_TABLE_CREATION_PATH)address_table/*

#################################################################################
# generate prebuilds for FPGA builds in config
#################################################################################
define PREBUILD_template =
 prebuild_$(1):  $(ADDRESS_TABLE_CREATION_PATH)config_$(1).yaml
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

$(ADDRESS_TABLE_CREATION_PATH)config_%.yaml : $(SLAVE_DEF_FILE_BASE)/%/config.yaml
	@yamllint -d "{extends: default,rules: {document-start: false,trailing-spaces: false,line-length: false,empty-lines: false,colons:  {max-spaces-before: -1, max-spaces-after: -1}}}" $<
	@rm -f $(ADDRESS_TABLE_CREATION_PATH)config*.yaml >& /dev/null
	@mkdir -p $(ADDRESS_TABLE_CREATION_PATH)
	@mkdir -p $(ADDRESS_TABLE_CREATION_PATH)address_tables/
	@mkdir -p $(KERNEL_BUILD_PATH) || :
	@mkdir -p $(SLAVE_DEF_FILE_BASE)/$*/autogen
	LD_LIBRARY_PATH=$(CACTUS_LD_PATH) ./build-scripts/preBuild.py \
			                     -s $^ \
				             -a $(ADDRESS_TABLE_CREATION_PATH) \
                                             -f config_$*.yaml \
                                             -m $(MAP_TEMPLATE_FILE) \
                                             $(USE_SIMPLE_PARSER) \
                                             -g $(CONFIGS_BASE_PATH)/$*/autogen
#

$(foreach prebuild,$(CONFIGS),$(eval $(call PREBUILD_template,$(prebuild))))

