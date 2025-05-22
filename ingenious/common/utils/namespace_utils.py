import importlib
import os
import pkgutil
from pathlib import Path
from sysconfig import get_paths

from ingenious.common.utils.module_importer import (
    ClassNotFoundInModuleError,
    ModuleImporter,
    ModuleImportError,
    ModuleNotFoundInNamespacesError,
)


def print_namespace_modules(namespace):
    """
    Print all modules found in a namespace.

    Args:
        namespace: The namespace to print modules for
    """
    package = importlib.import_module(namespace)
    if hasattr(package, "__path__"):
        for module_info in pkgutil.iter_modules(package.__path__):
            print(f"Found module: {module_info.name}")
    else:
        print(f"{namespace} is not a package. Importing now...")


def import_module_with_fallback(module_name):
    """
    Import a module with fallback to different namespaces.

    Args:
        module_name: The module name to import (without namespace)

    Returns:
        The imported module
    """
    try:
        importer = ModuleImporter()
        return importer.import_module(module_name)
    except ModuleNotFoundInNamespacesError as e:
        print(f"Module {module_name} not found in any namespace: {e}")
        return None
    except ModuleImportError as e:
        print(f"Error importing module {module_name}: {e}")
        return None


def import_class_with_fallback(module_name, class_name):
    """
    Import a class from a module with fallback to different namespaces.

    Args:
        module_name: The module name to import (without namespace)
        class_name: The name of the class to import

    Returns:
        The imported class

    Raises:
        ValueError: If the module or class cannot be found or imported
    """
    try:
        importer = ModuleImporter()
        return importer.import_class(module_name, class_name)
    except ModuleNotFoundInNamespacesError as e:
        raise ValueError(f"Module {module_name} not found in any namespace: {e}") from e
    except ClassNotFoundInModuleError as e:
        raise ValueError(
            f"Class {class_name} not found in module {module_name}: {e}"
        ) from e
    except ModuleImportError as e:
        raise ValueError(
            f"Error importing module {module_name}.{class_name}: {e}"
        ) from e


def get_path_from_namespace_with_fallback(path: str):
    """
    Get a path from the first namespace where it exists.

    Args:
        path: The relative path within a namespace

    Returns:
        The absolute path as a Path object, or None if not found
    """
    importer = ModuleImporter()
    namespace_paths = importer.get_namespace_paths()

    for namespace, base_path in namespace_paths.items():
        full_path = base_path / Path(path)
        if full_path.exists():
            return full_path

    return None


def get_file_from_namespace_with_fallback(module_name, file_name):
    """
    Get a file from a module in the first namespace where it exists.

    Args:
        module_name: The module name to look in (without namespace)
        file_name: The name of the file to read

    Returns:
        The file contents as a string, or None if not found
    """
    importer = ModuleImporter()
    namespace_paths = importer.get_namespace_paths()

    for namespace, base_path in namespace_paths.items():
        file_path = base_path / Path(module_name) / Path(file_name)
        if file_path.exists():
            with open(file_path, "r") as file:
                return file.read()

    return None


def get_path_from_namespace_with_fallback(path: str):
    """
    Get a path from the first namespace where it exists.

    Args:
        path: The relative path within a namespace

    Returns:
        The absolute path as a Path object, or None if not found
    """
    importer = ModuleImporter()
    namespace_paths = importer.get_namespace_paths()

    for namespace, base_path in namespace_paths.items():
        full_path = base_path / Path(path)
        if full_path.exists():
            return full_path

    return None


def get_inbuilt_api_routes():
    """
    Get the path to the in-built API routes.

    Returns:
        The path to the in-built API routes, or None if not found
    """
    working_dir = Path(os.getcwd()) / Path("ingenious") / Path("api") / Path("routes")
    install_dir = (
        Path(get_paths()["purelib"]) / Path("ingenious") / Path("api") / Path("routes")
    )

    for path in [working_dir, install_dir]:
        if path.exists():
            return path

    return None


def get_dir_roots():
    """
    Get a list of root directories for the project.

    Returns:
        A list of Path objects representing root directories
    """
    importer = ModuleImporter()
    namespace_paths = importer.get_namespace_paths()
    return list(namespace_paths.values())


def get_namespaces():
    """
    Get a list of namespace names for the project.

    Returns:
        A list of namespace names
    """
    importer = ModuleImporter()
    return importer.namespaces
