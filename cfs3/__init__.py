from cfs3.cftools import MetaFix, FileNameFix, CFSplitter, CFuploader
from cfs3.s3cmd import s3cmd
from importlib.metadata import version
from importlib.metadata import PackageNotFoundError


try:
    __version__ = version("cfs3")
except PackageNotFoundError as exc:
    msg = (
        "cfs3 package not found, please run `pip install -e .` before "
        "importing the package."
    )
    raise PackageNotFoundError(
        msg,
    ) from exc