#################################################################################
# Clean
#################################################################################
clean_address_tables:
	@rm -rf ${ADDRESS_TABLE_CREATION_PATH}address_tables
	@rm -rf ${ADDRESS_TABLE_CREATION_PATH}config*.yaml

#################################################################################
# simple generate rules for address tables
#################################################################################
define ADDRESS_TABLE_template =
 address_table_$(1): ${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table_$(1)/ ${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table_$(1)/address_apollo.xml
endef
ADRESSTABLEBUILDS=$(addprefix,address_table_,$(CONFIGS))
$(foreach addresstable,$(CONFIGS),$(eval $(call ADDRESS_TABLE_template,$(addresstable))))



#################################################################################
# address tables
#################################################################################

${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table_%/ :
	mkdir -p ${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table_$*/

${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table_%/address_apollo.xml: ${ADDRESS_TABLE_CREATION_PATH}config_%.yaml ${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table_%/
	./build-scripts/BuildAddressTable.py -l $< -t address_apollo.xml -o ${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table_$*/modules_$*/ -m modules_$*
	@rm -rf ${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table
	@ln -s address_table_$* ${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table

${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table_%/address_%.xml: ${ADDRESS_TABLE_CREATION_PATH}config_%.yaml ${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table_%/
	./build-scripts/BuildAddressTable.py -l $< -t address_$*.xml -o ${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table_$*/modules_$*/ -m modules_$*
	@rm -rf ${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table
	@ln -s address_tables/address_table_$* ${ADDRESS_TABLE_CREATION_PATH}address_tables/address_table


