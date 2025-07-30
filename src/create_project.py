from main import astroprojects_folder


class Frames:
    def __init__(self):
        self._lights_folder: str = ""
        self._darks: list[str] = []
        self._flats: list[str] = []

    def set_lights_folder(self, folder: str):
        pass


class Project:
    def __init__(self, name: str):
        self._name: str = name
        self._frames: list[Frames] = []
