import importlib
import pkgutil
import sys


def print_namespace_modules(namespace):
    package = importlib.import_module(namespace)
    if hasattr(package, '__path__'):
        for module_info in pkgutil.iter_modules(package.__path__):
            print(f"Found module: {module_info.name}")
    else:
        print(f"{namespace} is not a package. Importing now...")


def import_module_safely(module_name, class_name):
    print_namespace_modules(module_name)
    if not sys.modules.get(module_name):
        try:
            module = importlib.import_module(f"{module_name}")
            service_class = getattr(module, class_name)
            return service_class
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Unsupported chat conversation flow: {module_name}.{class_name}") from e
        except Exception as e:
            raise ValueError(f"An unexpected error occurred while importing {module_name}.{class_name}: {e}") from e
    else:
        module = importlib.import_module(f"{module_name}")
        service_class = getattr(module, class_name)   
        return service_class