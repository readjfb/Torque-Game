import os

class data_saver(object):
    """
    data_saver encapsulates a cache of data to be saved as well as the underlying code to save the data
    """
    def __init__(self, save_directory, state):
        """
        Construct a new 'data_saver' object.

        :param save_directory: The name of the directory within the /tests/ folder to be saved to
        :return: returns nothing
        """
        self.data_cache = []
        self.save_dir = os.getcwd() + "/tests/" + save_directory

        self.state = state

    def add_data(self, line):
        """
        Add a csv or other line to the cache of data to be saved

        :param line: the csv or other line
        :return: returns nothing
        """
        self.data_cache.append(line)

    def clear(self):
        """
        Clear the data cache

        :return: returns nothing
        """
        self.data_cache.clear()

    def save_data(self, mode):
        """
        Command that creates and writes a new file based on the cache

        :param mode: tell the object the mode, which informs the directory to
        be saved in

        :return: returns nothing
        """
        
        path = f"{self.save_dir}/{mode}/"

        try:
            os.makedirs(path)
        except OSError:
            # print ("Creation of the directory %s failed" % path)
            pass
        else:
            print ("Successfully created the directory %s" % path)

        i = 0
        while os.path.exists(f"{path}{mode}_data{i}.csv"):
            i += 1

        with open(f"{path}{mode}_data{i}.csv", "w") as file:
            for line in self.data_cache:
                file.write(line+"\n")

        print(f"Successfully wrote to file {path}{mode}_data{i}.csv")
        return


if __name__ == '__main__':
    save = data_saver("test_test")

    save.add_data("1,2,3,4")
    save.add_data("2,5,1,5")
    save.add_data("3,7,7,7")
    save.add_data("4,8,8,8")

    save.save_data("MVT_L")

        