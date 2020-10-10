import os


class Config(object):
    def __init__(self, args):
        self.__output_dir = args.directory
        self.__jungle = args.jungle

    @property
    def jungle(self):
        return self.__jungle

    @property
    def barrel_dir(self):
        return self.__output_dir

    def prepare_project_dir(self) -> None:
        """
        Put the project dir into a state where mbget can assume that all output
        locations are valid
        :return:
        """
        self.__build_output_dir()

    def open_file(self, name, mode, callback) -> None:
        with open(name, mode) as f:
            callback(f)

    def __build_output_dir(self):
        """
        Builds the output dir if its required.

        :return:
        """
        if not os.path.exists(self.__output_dir):
            os.mkdir(self.__output_dir)

    def read_file_content(self, file, callback):
        with open(file, "r") as f:
            callback(f)

    def write_text_file(self, file, callback):
        with open(file, "w") as f:
            callback(f)