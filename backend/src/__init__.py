from importlib import import_module
import sys

invictus_os_module = import_module("src.invictus_os")
sys.modules.setdefault("invictus_os", invictus_os_module)
