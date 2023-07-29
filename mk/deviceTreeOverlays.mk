#build dtbo files from dtsi files
DTSI_PATH ?= kernel/hw
DTSI_FILES_FULL_PATH = $(wildcard ${DTSI_PATH}/*.dtsi)
DTSI_FILES = $(notdir ${DTSI_FILES_FULL_PATH})

#place dtbo files in a subdirectory of the dtsi path
DTBO_PATH ?= ${DTSI_PATH}/dtbo
DTBO_FILES = $(patsubst %.dtsi,${DTBO_PATH}/%.dtbo,${DTSI_FILES})

DTC_FLAGS = -W "no-pci_device_reg" -W "no-pci_device_bus_num" -W "no-simple_bus_reg" -W "no-i2c_bus_reg" -W "no-spi_bus_reg" -W "no-avoid_default_addr_size" -W "no-reg_format"

overlays: ${DTBO_FILES}

clean_overlays:
	@rm -rf ${DTSI_PATH} >& /dev/null

${DTBO_PATH}/%.dtbo:${DTSI_PATH}/%.dtsi
	mkdir -p ${DTBO_PATH} >& /dev/null
	dtc ${DTC_FLAGS} -O dtb -o $@ -b 0 -@ $<
