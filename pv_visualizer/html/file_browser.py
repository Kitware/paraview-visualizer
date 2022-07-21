import os
import re
import logging

from trame.widgets.trame import ListBrowser

from paraview import simple

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ParaViewPathResolver:
    def __init__(
        self,
        basePath,
        name,
        excludeRegex=r"^\.|~$|^\$",
        groupRegex=r"[0-9]+\.",
        **kwargs,
    ):
        """
        Configure the way the WebFile browser will expose the server content.
         - basePath: specify the base directory (or directories) that we should start with, if this
         parameter takes the form: "name1=path1|name2=path2|...", then we will treat this as the
         case where multiple data directories are required.  In this case, each top-level directory
         will be given the name associated with the directory in the argument.
         - name: Name of that base directory that will show up on the web
         - excludeRegex: Regular expression of what should be excluded from the list of files/directories
        """
        self.multiRoot = False  # FIXME
        self.baseDirectory = basePath

        self.rootName = name
        self.pattern = re.compile(excludeRegex)
        self.gPattern = re.compile(groupRegex)

        if simple is None:
            return

        pxm = simple.servermanager.ProxyManager()
        self.directory_proxy = pxm.NewProxy("misc", "ListDirectory")
        self.fileList = simple.servermanager.VectorProperty(
            self.directory_proxy, self.directory_proxy.GetProperty("FileList")
        )
        self.directoryList = simple.servermanager.VectorProperty(
            self.directory_proxy, self.directory_proxy.GetProperty("DirectoryList")
        )

    def handleSingleRoot(self, baseDirectory, relativeDir, startPath=None):
        if simple is None:
            return {
                "label": "No ParaView",
                "files": [],
                "dirs": [],
                "groups": [],
                "path": "",
            }

        path = startPath or [self.rootName]
        if len(relativeDir) > len(self.rootName):
            relativeDir = relativeDir[len(self.rootName) + 1 :]
            path += relativeDir.replace("\\", "/").split("/")

        currentPath = os.path.normpath(os.path.join(baseDirectory, relativeDir))
        normBase = os.path.normpath(baseDirectory)

        if not currentPath.startswith(normBase):
            logger.critical("### CAUTION ==========================================")
            logger.critical(" Attempt to get to another root path ###")
            logger.critical("  => Requested:", relativeDir)
            logger.critical("  => BaseDir:", normBase)
            logger.critical("  => Computed path:", currentPath)
            logger.critical("### CAUTION ==========================================")
            currentPath = normBase

        self.directory_proxy.List(currentPath)
        self.directory_proxy.UpdatePropertyInformation()

        # build file/dir lists
        files = []
        if len(self.fileList) > 1:
            for f in self.fileList.GetData():
                if not re.search(self.pattern, f):
                    files.append({"label": f})
        elif len(self.fileList) == 1 and not re.search(
            self.pattern, self.fileList.GetData()
        ):
            files.append({"label": self.fileList.GetData()})

        dirs = []
        if len(self.directoryList) > 1:
            for d in self.directoryList.GetData():
                if not re.search(self.pattern, d):
                    dirs.append(d)
        elif len(self.directoryList) == 1 and not re.search(
            self.pattern, self.directoryList.GetData()
        ):
            dirs.append(self.directoryList.GetData())

        result = {
            "label": relativeDir,
            "files": files,
            "dirs": dirs,
            "groups": [],
            "path": path,
        }
        if relativeDir == ".":
            result["label"] = self.rootName

        # Filter files to create groups. Dicts are not orderable in Py3 - supply a key function.
        files.sort(key=lambda x: x["label"])
        groups = result["groups"]
        groupIdx = {}
        filesToRemove = []
        for file in files:
            fileSplit = re.split(self.gPattern, file["label"])
            if len(fileSplit) == 2:
                filesToRemove.append(file)
                gName = "*.".join(fileSplit)
                if gName in groupIdx:
                    groupIdx[gName]["files"].append(file["label"])
                else:
                    groupIdx[gName] = {"files": [file["label"]], "label": gName}
                    groups.append(groupIdx[gName])
        for file in filesToRemove:
            gName = "*.".join(re.split(self.gPattern, file["label"]))
            if len(groupIdx[gName]["files"]) > 1:
                files.remove(file)
            else:
                groups.remove(groupIdx[gName])

        return result

    def handleMultiRoot(self, relativeDir):
        if relativeDir == ".":
            return {
                "label": self.rootName,
                "files": [],
                "dirs": list(self.baseDirectoryMap),
                "groups": [],
                "path": [self.rootName],
            }

        pathList = relativeDir.replace("\\", "/").split("/")
        currentBaseDir = self.baseDirectoryMap[pathList[1]]
        if len(pathList) == 2:
            return self.handleSingleRoot(currentBaseDir, ".", pathList)
        else:  # must be greater than 2
            return self.handleSingleRoot(
                currentBaseDir, "/".join([pathList[0]] + pathList[2:]), pathList[0:2]
            )

    def list_directory(self, relativeDir="."):
        """
        RPC Callback to list a server directory relative to the basePath
        provided at start-up.
        """
        if self.multiRoot:
            return self.handleMultiRoot(relativeDir)
        else:
            return self.handleSingleRoot(self.baseDirectory, relativeDir)


class AbstractFileBrowser(ListBrowser):
    def __init__(self, resolver, on_load_file=None, namespace="file_browser", **kwargs):
        self._resolver = resolver
        self._on_load_file = on_load_file
        self._key_open_file = f"{namespace}_open"
        self._key_path = f"{namespace}_path"
        self._key_listing = f"{namespace}_listing"

        super().__init__(
            list=(self._key_listing, []),
            path=(self._key_path, []),
            click=(self._update_path, "[]", "$event"),
            **kwargs,
        )
        # "path_icon",
        # "path_selected_icon",
        # "filter_icon",
        # "filter",
        # "path",
        # "list",

    def _update_listing(self):
        path_tokens = self.server.state[self._key_path]
        base_path = "/".join(path_tokens) if len(path_tokens) > 1 else "."
        directory_meta = self._resolver.list_directory(base_path)
        listing = []

        # add directories
        directories = directory_meta.get("dirs", [])
        for directory in directories:
            listing.append(
                {
                    "text": directory,
                    "value": directory,
                    "type": "Directory",
                    "prependIcon": "mdi-folder",
                    "appendIcon": "mdi-chevron-right",
                }
            )

        # add groups
        groups = directory_meta.get("groups", [])
        for group in groups:
            listing.append(
                {
                    "text": group.get("label"),
                    "value": group.get("files"),
                    "type": "Group",
                    "prependIcon": "mdi-file-document-multiple-outline",
                }
            )

        # add files
        files = directory_meta.get("files", [])
        for file in files:
            listing.append(
                {
                    "text": file.get("label"),
                    "value": file.get("label"),
                    "type": "File",
                    "prependIcon": "mdi-file-document-outline",
                }
            )

        self.server.state[self._key_listing] = listing

    def _update_path(self, type, value):
        if type == "Directory":
            current_path = self.server.state[self._key_path]
            new_path = []
            new_path.extend(current_path)
            new_path.append(value)
            self.server.state[self._key_path] = new_path
            self._update_listing()
        elif type == "path":
            new_path = value.split("/")
            self.server.state[self._key_path] = new_path
            self._update_listing()
        elif type == "Group":
            path_with_root = list(self.server.state[self._key_path])
            path_with_root.pop(0)  # remove Home/
            current_path = "/".join(path_with_root)
            files_to_load = []
            for file in value:
                files_to_load.append(f"{current_path}/{file}")
            if self._on_load_file:
                self._on_load_file(files_to_load)
        elif type == "File":
            path_with_root = list(self.server.state[self._key_path])
            path_with_root.pop(0)  # remove Home/
            if len(path_with_root):
                current_path = "/".join(path_with_root)
                file_to_load = f"{current_path}/{value}"
            else:
                file_to_load = value

            if self._on_load_file:
                self._on_load_file(file_to_load)
        else:
            logger.info(f"need to handle {type}: {value}")


class ParaViewFileBrowser(AbstractFileBrowser):
    def __init__(
        self,
        base_path,
        root_name="Home",
        on_load_file=None,
        exclude_regex=r"^\.|~$|^\$",
        group_regex=r"[0-9]+\.",
        namespace="file_browser",
        **kwargs,
    ):
        self._pv_resolver = ParaViewPathResolver(
            base_path, root_name, exclude_regex, group_regex
        )
        self._on_load_file = on_load_file
        super().__init__(self._pv_resolver, self._on_load_file, namespace, **kwargs)

        self.server.state[self._key_path] = [root_name]
        self._update_listing()
