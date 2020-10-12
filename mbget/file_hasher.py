import hashlib
from typing import BinaryIO


class FileHasher(object):
    BLOCK_SIZE = 65535

    def __init__(self):
        pass

    def match(self, file_path, expected_hash) -> bool:
        return self.hash_file(file_path) == expected_hash

    def hash_file(self, file_path) -> str:
        """

        :param file_path:
        :return:
        """
        with open(file_path, "rb") as f:
            return self.__hash_file(f)

    def __hash_file(self, f: BinaryIO) -> str:
        h = hashlib.sha256()
        fb = f.read(self.BLOCK_SIZE)
        while len(fb) > 0:
            h.update(fb)
            fb = f.read(self.BLOCK_SIZE)

        return h.hexdigest()
