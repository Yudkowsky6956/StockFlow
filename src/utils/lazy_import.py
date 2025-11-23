import importlib


def lazy_import(module_name, attr_name, package=None):
    """Ленивый импорт: module_name может быть относительным, тогда нужно указать package."""
    class LazyLoader:
        _loaded_attr = None

        def _load(self):
            if self._loaded_attr is None:
                module = importlib.import_module(module_name, package=package)
                self._loaded_attr = getattr(module, attr_name)
            return self._loaded_attr

        def __getattr__(self, item):
            return getattr(self._load(), item)

        def __call__(self, *args, **kwargs):
            return self._load()(*args, **kwargs)

    return LazyLoader()