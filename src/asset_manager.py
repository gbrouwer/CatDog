import os

class AssetManager:
    """
    Provides a standardized way to resolve paths to global system assets.
    Prevents modules from hardcoding relative filesystem paths.
    """

    # Assume assets/ folder is at project root (sibling to src/)
    BASE_ASSET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))

    @classmethod
    def resolve(cls, *path_parts):
        """
        Resolve one or more path parts into a full asset path.
        Example: AssetManager.resolve("sounds", "boot.wav")
        """
        print(f"[DEBUG] Resolving asset path from __file__ = {__file__}")
        print(f"[DEBUG] Asset base path = {cls.BASE_ASSET_PATH}")
        return os.path.join(cls.BASE_ASSET_PATH, *path_parts)

    @classmethod
    def exists(cls, *path_parts):
        """
        Check if an asset exists.
        Example: AssetManager.exists("sounds", "boot.wav")
        """
        return os.path.isfile(cls.resolve(*path_parts))

    @classmethod
    def list_assets(cls, *subfolder_parts):
        """
        List all assets under a specific subfolder.
        Example: AssetManager.list_assets("sounds")
        """
        folder_path = cls.resolve(*subfolder_parts)
        if not os.path.isdir(folder_path):
            return []
        return os.listdir(folder_path)