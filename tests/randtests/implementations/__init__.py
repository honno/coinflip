from .dj import testmap as dj_testmap
from .nist import testmap as nist_testmap
from .sgr import testmap as sgr_testmap

__all__ = ["testmaps"]

testmaps = {"nist": nist_testmap, "sgr": sgr_testmap, "dj": dj_testmap}
