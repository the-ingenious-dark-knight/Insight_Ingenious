"""
Dependency Injection Container for Ingenious.

This module provides a container for dependency injection, following the
Service Locator pattern while enabling proper dependency management.
"""

from typing import Any, Dict, Type, TypeVar, cast

T = TypeVar("T")


class DIContainer:
    """
    Dependency Injection Container.

    This container manages dependencies and their instantiation, allowing for
    better inversion of control and testability.
    """

    def __init__(self):
        self._bindings: Dict[Type, Type] = {}
        self._instances: Dict[Type, Any] = {}
        self._factories: Dict[Type, callable] = {}

    def bind(self, interface: Type[T], implementation: Type[T]) -> None:
        """
        Bind an interface to its implementation.

        Args:
            interface: The interface type to bind
            implementation: The implementation type to bind to the interface
        """
        self._bindings[interface] = implementation

    def bind_instance(self, interface: Type[T], instance: T) -> None:
        """
        Bind an interface to an existing instance.

        Args:
            interface: The interface type to bind
            instance: The instance to bind to the interface
        """
        self._instances[interface] = instance

    def bind_factory(self, interface: Type[T], factory: callable) -> None:
        """
        Bind an interface to a factory function.

        Args:
            interface: The interface type to bind
            factory: A callable that creates an instance of the interface
        """
        self._factories[interface] = factory

    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve an interface to its implementation instance.

        Args:
            interface: The interface type to resolve

        Returns:
            An instance of the implementation bound to the interface

        Raises:
            KeyError: If the interface is not bound
        """
        # If we already have an instance, return it
        if interface in self._instances:
            return cast(T, self._instances[interface])

        # If we have a factory, use it to create an instance
        if interface in self._factories:
            instance = self._factories[interface]()
            self._instances[interface] = instance
            return cast(T, instance)

        # If we have a binding, instantiate it
        if interface in self._bindings:
            implementation = self._bindings[interface]
            instance = implementation()
            self._instances[interface] = instance
            return cast(T, instance)

        # If we don't have a binding, but the interface is a concrete class,
        # we can instantiate it directly
        if isinstance(interface, type):
            instance = interface()
            self._instances[interface] = instance
            return cast(T, instance)

        raise KeyError(f"No binding found for {interface}")


# Singleton instance
_container = DIContainer()


def get_container() -> DIContainer:
    """
    Get the global DIContainer instance.

    Returns:
        The global DIContainer instance
    """
    return _container
