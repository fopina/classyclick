import importlib
import pkgutil


def discover_commands(commands_package: str):
    """Import every command module, including ones nested in subpackages."""
    package = importlib.import_module(commands_package)
    # str() required because of py3.10
    for _, module_name, _ in pkgutil.walk_packages(package.__path__, f'{commands_package}.'):
        importlib.import_module(module_name)
