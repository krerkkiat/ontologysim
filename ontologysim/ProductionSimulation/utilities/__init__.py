from importlib import import_module

from .event import EventUtilities
from .init import IniDict, IniString, Init
from .path import PathTest, sanitize_path


def import_class(path: str, parent: type | None = None) -> type:
    """
    Import the module from path.

    The `path` must be in the format of `<module-path>:<name>`.
    The imported name must be a class otherwise ValueError is raised.

    If `parent` is not None, the imported class is check if it is
    a subclass of the `parent`.
    """
    tokens = path.split(":")
    if len(tokens) != 2:
        raise ValueError(
            f"'{path}' is not in the expected format. It must be in the format of '<module-path>:<name>'"
        )

    module_path, name = tokens
    try:
        # NOTE(KC): We will be running foreign code. The web app GUI
        # may not be deployable for multiple users environment.
        #
        # Maybe the controller's logic can be in WebAssembly (from
        # Rust or Python itself) and run with a webassembly runtime?
        module = import_module(module_path, None)

        if not hasattr(module, name):
            raise ValueError(f"Cannot find '{name}' in '{module_path}'")

        klass = getattr(module, name)
        if not isinstance(klass, type):
            raise ValueError(f"'{name}' is not a Class.")

        if parent is not None:
            if not issubclass(klass, parent):
                raise ValueError(f"'{name}' is not a sub-class of '{parent}'.")

        return klass

    except ImportError as e:
        raise ValueError(f"Cannot import module '{module_path}'.") from e


__all__ = [
    EventUtilities,
    Init,
    IniString,
    IniDict,
    sanitize_path,
    import_class,
    PathTest,
]
