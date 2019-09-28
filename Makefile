# ###### EDIT #####################
# #Directory with ui and resource files
# UI_DIR = ./
# RESOURCE_DIR = ./res
#
# COMPILED_DIR = ./
#
# RESOURCES = resources.qrc
# UI_FILES = mainwindow.ui
#
#
# #################################
# # DO NOT EDIT FOLLOWING
#
# COMPILED_UI = $(UI_FILES:%.ui=$(COMPILED_DIR)/%.py)
# COMPILED_RESOURCES = $(RESOURCES:%.qrc=$(COMPILED_DIR)/%.py)
#
# all : resources ui
#
# resources : $(COMPILED_RESOURCES)
#
# ui : $(COMPILED_UI)
#
# $(COMPILED_DIR)/%.py : $(RESOURCE_DIR)/%.ui
# 	$(PYUIC) $< -o $@
#
# $(COMPILED_DIR)/%.py : $(RESOURCE_DIR)/%.qrc
# 	$(PYRCC) $< -o $@

UIFILES := $(wildcard *.ui)
PYUIFILES := $(UIFILES:.ui=.py)

RESFILES := $(wildcard *.qrc)
PYRESFILES := $(RESFILES:.qrc=_rc.py)

PYRCC := pyrcc5
PYUIC := pyuic5

.PHONY: all
all: $(PYUIFILES) $(PYRESFILES)

%.py: %.ui
	$(PYUIC) $< -o $@
# --resource-suffix

%_rc.py: %.qrc
	$(PYRCC) $< -o $@

# clean :
# 	$(RM) $(COMPILED_UI) $(COMPILED_RESOURCES) $(COMPILED_UI:.py=.pyc) $(COMPILED_RESOURCES:.py=.pyc)
