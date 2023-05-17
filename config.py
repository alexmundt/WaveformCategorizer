import configparser



class Configuration(object):
    """docstring for Configuration."""

    def __init__(self, filename = "config.ini"):
        super(Configuration, self).__init__()
        self.filename = filename
        try:
            self.read_file(self.filename)
            print("File read succesfully.")
        except Exception as ex:
            print(ex)
            print(f"Config file not read succesfully: {ex}\nGenerating generic"+
                " configuration")

            self.config = configparser.ConfigParser()
            self.config["OPTIONS"] = {}

    def write_to_file(self, filename=None):
        if filename == None:
            filename = self.filename
        with open(filename, "w") as configfile:
            self.config.write(configfile)

    def set_value(self, option, value):
        """ set option in the config to value
        """
        value = str(value)
        self.config.set("OPTIONS", option, value)

    def read_file(self, filename=None):
        """ reading a configfile
        """
        if filename == None:
            filename = self.filename
        read_config = configparser.ConfigParser()
        read_config.read(filename)
        self.config = read_config

    def printout(self):
        for key in self.config["OPTIONS"]:
            print_string = f"{key} : {self.config['OPTIONS'][key]}"
            print(print_string)

    def get_option_value(self, option):
        try:
            value = self.config["OPTIONS"][option]
            print(f"value : {value}")
            if "." in value:
                value = float(value)
            else:
                value = int(value)
        except KeyError:
            print(f"KeyError: key={option} does not exist. Returning None")
            value = None
        return value
