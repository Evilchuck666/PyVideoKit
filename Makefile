AUR_DIR  := AUR
CLI_DIR  := PyVideoKit-CLI
GUI_DIR  := PyVideoKit-GUI
LIBS_DIR := PyVideoKit-Libs
META_DIR := .

.PHONY: help aur build-all build-cli build-gui build-libs build-meta \
        clean-all clean-aur clean-cli clean-gui clean-libs clean-meta \
        clean-pkgs install-all install-cli install-gui install-libs \
        uninstall-all uninstall-cli uninstall-gui uninstall-libs

help:
	@echo "Available targets:"
	@echo "  aur          	Build and install the PyVideoKit AUR package from the AUR/ directory"
	@echo "  build-all    	Build all wheel packages and clean artifacts"
	@echo "  build-cli    	Build the PyVideoKit-CLI wheel and clean artifacts"
	@echo "  build-gui    	Build the PyVideoKit-GUI wheel and clean artifacts"
	@echo "  build-libs   	Build the PyVideoKit-Libs wheel and clean artifacts"
	@echo "  build-meta   	Build the PyVideoKit meta-package wheel and clean artifacts"
	@echo "  clean-all    	Remove build artifacts from all projects"
	@echo "  clean-aur    	Remove build artifacts from PyVideoKit-AUR"
	@echo "  clean-cli    	Remove build artifacts from PyVideoKit-CLI"
	@echo "  clean-gui    	Remove build artifacts from PyVideoKit-GUI"
	@echo "  clean-libs   	Remove build artifacts from PyVideoKit-Libs"
	@echo "  clean-meta   	Remove build artifacts from the PyVideoKit meta-package"
	@echo "  clean-pkgs   	Remove all generated wheel files from PKGs/"
	@echo "  help         	Show this help message"
	@echo "  install-all  	Install all wheel packages from PKGs/"
	@echo "  install-cli  	Install the PyVideoKit-CLI wheel from PKGs/"
	@echo "  install-gui  	Install the PyVideoKit-GUI wheel from PKGs/"
	@echo "  install-libs 	Install the PyVideoKit-Libs wheel from PKGs/"
	@echo "  uninstall-all  Uninstall all PyVideoKit packages"
	@echo "  uninstall-cli  Uninstall the PyVideoKit-CLI package"
	@echo "  uninstall-gui  Uninstall the PyVideoKit-GUI package"
	@echo "  uninstall-libs Uninstall the PyVideoKit-Libs package"

aur:
	cd $(AUR_DIR) && makepkg -si
	$(MAKE) clean-aur

build-all: build-libs build-cli build-gui build-meta

build-cli:
	python -m build --wheel $(CLI_DIR)
	mkdir -p PKGs
	mv $(CLI_DIR)/dist/*.whl PKGs/
	$(MAKE) clean-cli

build-gui:
	python -m build --wheel $(GUI_DIR)
	mkdir -p PKGs
	mv $(GUI_DIR)/dist/*.whl PKGs/
	$(MAKE) clean-gui

build-libs:
	python -m build --wheel $(LIBS_DIR)
	mkdir -p PKGs
	mv $(LIBS_DIR)/dist/*.whl PKGs/
	$(MAKE) clean-libs

build-meta:
	python -m build --wheel $(META_DIR)
	mkdir -p PKGs
	mv dist/*.whl PKGs/
	$(MAKE) clean-meta

clean-all: clean-cli clean-gui clean-libs clean-meta

clean-aur:
	rm -rf $(AUR_DIR)/src $(AUR_DIR)/pkg $(AUR_DIR)/*.pkg.tar.zst $(AUR_DIR)/PyVideoKit-Libs $(AUR_DIR)/PyVideoKit-CLI $(AUR_DIR)/PyVideoKit-GUI

clean-cli:
	rm -rf $(CLI_DIR)/dist $(CLI_DIR)/build $(CLI_DIR)/src/PyVideoKit_CLI.egg-info

clean-gui:
	rm -rf $(GUI_DIR)/dist $(GUI_DIR)/build $(GUI_DIR)/src/PyVideoKit_GUI.egg-info

clean-libs:
	rm -rf $(LIBS_DIR)/dist $(LIBS_DIR)/build $(LIBS_DIR)/src/PyVideoKit_Libs.egg-info

clean-meta:
	rm -rf dist/ build/ PyVideoKit.egg-info/

clean-pkgs:
	rm -rf PKGs/

install-all: install-libs install-cli install-gui

install-cli:
	$(MAKE) build-cli
	pip install --break-system-packages PKGs/pyvideokit_cli-*.whl

install-gui:
	$(MAKE) build-gui
	pip install --break-system-packages PKGs/pyvideokit_gui-*.whl

install-libs:
	$(MAKE) build-libs
	pip install --break-system-packages PKGs/pyvideokit_libs-*.whl

uninstall-all: uninstall-cli uninstall-gui uninstall-libs

uninstall-cli:
	pip uninstall -y PyVideoKit-CLI --break-system-packages

uninstall-gui:
	pip uninstall -y PyVideoKit-GUI --break-system-packages

uninstall-libs:
	pip uninstall -y PyVideoKit-Libs --break-system-packages
