from trame.assets.local import LocalFileManager

asset_manager = LocalFileManager(__file__)
asset_manager.url("icon", "./pv_logo.svg")
asset_manager.url("icon_delete", "./database-remove-outline.svg")
