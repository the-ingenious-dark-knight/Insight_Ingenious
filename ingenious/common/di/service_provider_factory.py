"""
Service Provider Factory module.

This module provides a factory for creating service providers with proper dependency injection.
It follows the Factory and Service Locator patterns.
"""

from typing import Dict, Generic, Type, TypeVar

from ingenious.domain.model.config import Config

T = TypeVar("T")
S = TypeVar("S")


class ServiceProviderFactory(Generic[T, S]):
    """
    Factory for creating service providers with appropriate configuration.

    This class follows the Factory pattern and uses dependency injection for better testability.
    It is generic over the interface type and the parameter type.
    """

    def __init__(
        self, interface_type: Type[T], implementation_resolver: callable, config: Config
    ):
        """
        Initialize the ServiceProviderFactory.

        Args:
            interface_type: The interface type this factory provides
            implementation_resolver: Function to resolve implementation instances
            config: The application configuration
        """
        self.interface_type = interface_type
        self.implementation_resolver = implementation_resolver
        self.config = config
        self._instances: Dict[str, T] = {}

    def get(self, param: S = None) -> T:
        """
        Get a service provider instance.

        Args:
            param: Optional parameter to differentiate service providers

        Returns:
            A service provider instance
        """
        key = str(param) if param is not None else ""

        if key not in self._instances:
            self._instances[key] = self.implementation_resolver(param)

        return self._instances[key]
