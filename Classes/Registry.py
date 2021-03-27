from winreg import ConnectRegistry, HKEY_LOCAL_MACHINE, EnumKey, OpenKey, QueryValueEx, EnumValue
from Classes.Configuration import Configuration


class Registry:
    __registry_id: int = HKEY_LOCAL_MACHINE

    def getInstallLocation(self, program_name: str):
        fetcher, value_id = Configuration.getRegistryKey(program_name)
        registry = ConnectRegistry(None, self.__registry_id)

        path = ""

        if isinstance(fetcher, tuple):
            fetcher = [fetcher]

        out = None
        try:
            if isinstance(fetcher, str):
                out = EnumValue(OpenKey(registry, fetcher), 0)
            elif isinstance(fetcher, list):
                for slice in fetcher:
                    slice = tuple(slice) if isinstance(slice, list) else slice

                    if isinstance(slice, str):
                        path += f"\\{slice}"
                        continue
                    elif isinstance(slice, tuple) and len(slice) == 2:
                        reg_key, slice_id = slice
                        path += ('\\' if path != '' else '')
                        path += reg_key

                        if isinstance(slice_id, int):

                            if slice != fetcher[-1]:

                                path += f"\\{EnumKey(OpenKey(registry, path), slice_id)}"
                            else:
                                out = EnumKey(OpenKey(registry, path), slice_id)
                        elif isinstance(slice_id, str):
                            if slice != tuple(fetcher[-1]):
                                path += f"\\{QueryValueEx(OpenKey(registry, path), slice_id)}"
                            else:
                                out = QueryValueEx(OpenKey(registry, path), slice_id)

        finally:
            if out is not None:
                return out[value_id]
