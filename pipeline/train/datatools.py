from io import BytesIO

from settings import FileSettings


def walk_dir(path: Path) -> Iterator:
    """loops recursively through a folder

    Args:
        path (Path): folder to loop trough. If a directory
            is encountered, loop through that recursively.

    Yields:
        Generator: all paths in a folder and subdirs.
    """

    for p in Path(path).iterdir():
        if p.is_dir():
            yield from walk_dir(p)
            continue
        yield p.resolve()


class FileHandler:
    def __init__(self, settings: FileSettings) -> None:
        self.bucket = settings.bucket
        self.data_dir = settings.datadir

    # def _get_blob(self, filepath: Path) -> storage.blob.Blob:
    #     client = storage.Client()
    #     bucket = client.get_bucket(self.bucket)
    #     blob = bucket.blob(str(filepath))
    #     return blob

    # def _get_io(self, filepath: Path) -> BytesIO:
    #     logger.info(f"Loading {filepath} from blob")
    #     bytestream = BytesIO()
    #     blob = self._get_blob(filepath)
    #     blob.download_to_file(bytestream)
    #     bytestream.seek(0)
    #     return bytestream

    # def blobtolocal(self, filepath: Path, data_dir: Path) -> None:
    #     blob = self._get_blob(filepath)
    #     path = data_dir / filepath
    #     logger.info(f"downloading blob to {path}")
    #     blob.download_to_filename(path)

    def load_from_dir(self, filepath: Path) -> pl.DataFrame:
        path = self.data_dir / filepath
        logger.info(f"loading file from {path}")
        if filepath.suffix == ".parq":
            data = pl.read_parquet(path)
        elif filepath.suffix == ".csv":
            data = pl.read_csv(path)
        else:
            raise ValueError("The file is expected to be .parq or .csv")

        return data

    def load_from_blob(self, filepath: Path, backend: str = "polars") -> DataFrame:
        bytestream = self._get_io(filepath)
        if backend == "polars":
            data = pl.read_parquet(bytestream)
        else:
            data = pd.read_parquet(bytestream)
        return data

    def _get_buf_size(self, buf: BytesIO) -> Tuple[int, BytesIO]:
        buf.seek(0, 2)
        total_size = buf.tell()
        buf.seek(0)
        return total_size, buf

    def save_to_blob(self, df: pl.DataFrame, filepath: Path) -> None:
        bytestream = BytesIO()
        logger.info("write to io")
        df.write_parquet(bytestream)
        total_size, bytestream = self._get_buf_size(bytestream)
        logger.info(f"Total size {(total_size / (1024*1024)):.3f} Mb")
        blob = self._get_blob(filepath)
        blob.upload_from_file(bytestream)
        logger.success(f"Finished {filepath}")
