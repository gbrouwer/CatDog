# launcher.py

from log import log, log_error
import argparse
import asyncio
import json
import sys
import importlib

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", required=True, help="Full class path of the module to launch.")
    parser.add_argument("--params", required=False, help="JSON-encoded parameters for the module.")
    args = parser.parse_args()

    module_class_path = args.module
    params = json.loads(args.params) if args.params else {}

    module_path, class_name = module_class_path.rsplit('.', 1)
    log("Launcher", module_path)
    log("Launcher", class_name)

    try:
        imported_module = importlib.import_module(module_path)
        ModuleClass = getattr(imported_module, class_name)

        module_instance = ModuleClass(**params)

        if hasattr(module_instance, 'boot'):
            await module_instance.boot()
        await module_instance.start()

        log("Launcher", f"{class_name} started. Running indefinitely...")
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        log_error("Launcher", f"Module {class_name} crashed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
