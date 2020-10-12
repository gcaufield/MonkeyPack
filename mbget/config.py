import os


class Config(object):
    def __init__(self, args):
        self.__token = args.token
        self.__package = args.package
        self.__output_dir = args.directory
        self.__jungle = args.jungle

    @property
    def jungle(self) -> str:
        return self.__jungle

    @property
    def package(self) -> str:
        return self.__package

    @property
    def barrel_dir(self) -> str:
        return self.__output_dir

    @property
    def token(self) -> str:
        return self.__token

    def prepare_project_dir(self) -> None:
        """
        Put the project dir into a state where mbget can assume that all output
        locations are valid
        :return:
        """
        self.__build_output_dir()

    def __build_output_dir(self):
        """
        Builds the output dir if its required.

        :return:
        """
        if not os.path.exists(self.__output_dir):
            os.mkdir(self.__output_dir)

    @staticmethod
    def open_file(name, mode, callback) -> None:
        with open(name, mode) as f:
            callback(f)
