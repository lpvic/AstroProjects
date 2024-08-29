from pathlib import Path


class FolderStructure:
    def __init__(self, root_folder: str | Path) -> None:
        self._root = Path(root_folder)
        self._sources = self._root / 'sources'
        self._dark_sources = self._sources / 'darks'
        self._flat_sources = self._sources / 'flats'
        self._light_sources = self._sources / 'lights'
        self._masters = self.root / 'masters'
        self._master_darks = self._masters / 'darks'
        self._master_flats = self._masters / 'flats'
        self._projects = self._root / 'projects'
        self._metadata = self._root / 'metadata'
        self._sources_dict = {'dark': self._dark_sources, 'flat': self._flat_sources, 'light': self._light_sources}
        self._masters_dict = {'dark': self._master_darks, 'flat': self._master_flats}

        for f in [self._dark_sources, self._flat_sources, self._light_sources,
                  self._master_darks, self._master_flats, self._projects, self._metadata]:
            f.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    @property
    def sources(self) -> Path:
        return self._sources

    @property
    def dark_sources(self) -> Path:
        return self._dark_sources

    @property
    def flat_sources(self) -> Path:
        return self._flat_sources

    @property
    def light_sources(self) -> Path:
        return self._light_sources

    @property
    def masters(self) -> Path:
        return self._masters

    @property
    def master_darks(self) -> Path:
        return self._master_darks

    @property
    def master_flats(self) -> Path:
        return self._master_flats

    @property
    def projects(self) -> Path:
        return self._projects

    @property
    def metadata(self) -> Path:
        return self._metadata

    @property
    def sources_dict(self) -> dict[str, Path]:
        return self._sources_dict

    @property
    def masters_dict(self) -> dict[str, Path]:
        return self._masters_dict
