AUR_DIR  := AUR
CLI_DIR  := PyVideoKit-CLI
GUI_DIR  := PyVideoKit-GUI
LIBS_DIR := PyVideoKit-Libs
META_DIR := .

.PHONY: help aur build-all build-cli build-gui build-libs build-meta \
        clean-all clean-aur clean-cli clean-gui clean-libs clean-meta \
        install-all install-cli install-gui install-libs upload

help:
	@echo "Targets disponibles:"
	@echo "  aur          Construye e instala el paquete AUR de PyVideoKit desde el directorio AUR/"
	@echo "  build-all    Construye todos los paquetes wheel y limpia artefactos"
	@echo "  build-cli    Construye el paquete wheel de PyVideoKit-CLI y limpia artefactos"
	@echo "  build-gui    Construye el paquete wheel de PyVideoKit-GUI y limpia artefactos"
	@echo "  build-libs   Construye el paquete wheel de PyVideoKit-Libs y limpia artefactos"
	@echo "  build-meta   Construye el paquete wheel del meta-paquete PyVideoKit y limpia artefactos"
	@echo "  clean-all    Elimina los artefactos de build de todos los proyectos"
	@echo "  clean-aur    Elimina los artefactos de build de PyVideoKit-AUR"
	@echo "  clean-cli    Elimina los artefactos de build de PyVideoKit-CLI"
	@echo "  clean-gui    Elimina los artefactos de build de PyVideoKit-GUI"
	@echo "  clean-libs   Elimina los artefactos de build de PyVideoKit-Libs"
	@echo "  clean-meta   Elimina los artefactos de build del meta-paquete PyVideoKit"
	@echo "  help         Muestra esta ayuda"
	@echo "  install-all  Instala todos los paquetes wheel desde PKGs/"
	@echo "  install-cli  Instala el wheel de PyVideoKit-CLI desde PKGs/"
	@echo "  install-gui  Instala el wheel de PyVideoKit-GUI desde PKGs/"
	@echo "  install-libs Instala el wheel de PyVideoKit-Libs desde PKGs/"
	@echo "  upload       Sube todos los wheels de PKGs/ a PyPI"

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

upload:
	twine upload PKGs/*.whl
