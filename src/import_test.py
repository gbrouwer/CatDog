import importlib

def quick_import_check():
    try:
        imported_module = importlib.import_module("modules.actuators.emitter.sound.pcspeaker")
        print("[SUCCESS] Import succeeded: modules.actuators.emitter.sound.pcspeaker")
    except ModuleNotFoundError as e:
        print("[ERROR] ModuleNotFoundError:", e)
    except Exception as e:
        print("[ERROR] Other Exception:", e)

if __name__ == "__main__":
    quick_import_check()
