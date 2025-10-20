import importlib
import pkgutil

def register_all_handlers(app):
    """
    Автоматично імпортує всі модулі з handlers/ і викликає їхню функцію register_*(app)
    """
    package = __name__
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        full_module = f"{package}.{module_name}"
        module = importlib.import_module(full_module)

        # Шукаємо функцію типу register_*
        for attr in dir(module):
            if attr.startswith("register_"):
                register_func = getattr(module, attr)
                if callable(register_func):
                    register_func(app)
