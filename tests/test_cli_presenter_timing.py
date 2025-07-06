from cli.presenters.cli_presenter import CliPresenter

# Mock i18n and color_service for testing
class DummyI18n:
    _messages = {'HELLO': 'Hola', 'ERROR': 'Error', 'WARN': 'Advertencia'}
    _default_lang = 'es'
    def get(self, key):
        return self._messages.get(key, key)

class DummyColor:
    def colorize(self, msg, color):
        return f"<{color}>{msg}</{color}>"

class DummyLogger:
    def info(self, msg, **_kwargs):
        print(f"[INFO] {msg}")
    def error(self, msg, **_kwargs):
        print(f"[ERROR] {msg}")
    def warning(self, msg, **_kwargs):
        print(f"[WARN] {msg}")
    def debug(self, msg, **_kwargs):
        print(f"[DEBUG] {msg}")

if __name__ == "__main__":
    presenter = CliPresenter(i18n=DummyI18n(), color_service=DummyColor(), logger_instance=DummyLogger())
    print("--- Modo DEV ---")
    presenter.print_error("Esto es un error de prueba", dev_mode=True)
    presenter.print_warning("Esto es un warning de prueba", dev_mode=True)
    presenter.print_debug("Esto es un debug de prueba", dev_mode=True)
    presenter.print_success("Esto es un success de prueba", dev_mode=True)
    print("--- Modo normal ---")
    presenter.print_error("Esto es un error normal", dev_mode=False)
    presenter.print_warning("Esto es un warning normal", dev_mode=False)
    presenter.print_debug("Esto es un debug normal", dev_mode=False)
    presenter.print_success("Esto es un success normal", dev_mode=False)
    print("--- INPUT (no debe mostrar tiempo) ---")
    # No se puede testear input en modo script, pero se puede verificar que no hay decorador
