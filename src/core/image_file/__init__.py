# import io
# import sys

from .exceptions import FilemakerError
from .image_file import ImageFile
from .metadata_manager import ImageMetadataManager


# class FilterOutSpecificWarnings(io.StringIO):
#     def write(self, msg):
#         if "Data area exceeds data buffer" not in msg:
#             sys.__stdout__.write(msg)
#
# sys.stdout = FilterOutSpecificWarnings()
# sys.stderr = FilterOutSpecificWarnings()