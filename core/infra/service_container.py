"""
Service Container for Dependency Injection
"""

from typing import Dict, Type, Any, Callable
import threading


class ServiceContainer:
    """Singleton service container for dependency injection"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ServiceContainer, cls).__new__(cls)
                    cls._instance._services = {}
                    cls._instance._factories = {}
        return cls._instance
    
    def register_singleton(self, name: str, service_class: Type, *args, **kwargs):
        """Register a singleton service"""
        self._services[name] = service_class(*args, **kwargs)
    
    def register_factory(self, name: str, factory: Callable):
        """Register a factory function"""
        self._factories[name] = factory
    
    def get(self, name: str) -> Any:
        """Get service instance"""
        if name in self._services:
            return self._services[name]
        elif name in self._factories:
            instance = self._factories[name]()
            self._services[name] = instance
            return instance
        else:
            raise KeyError(f"Service '{name}' not registered")
    
    def clear(self):
        """Clear all services"""
        self._services.clear()
        self._factories.clear()


# Global container instance
container = ServiceContainer()
Container = ServiceContainer  # Alias for backward compatibility
