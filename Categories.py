from os import listdir
import pandas as pd
from tqdm import tqdm
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog as fd



class Category(object):
    """docstring for Category."""

    def __init__(self):
        super(Category, self).__init__()

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value


class TagsContainer(object):
    """docstring for TagsContainer."""

    def __init__(self, list_events):
        super(TagsContainer, self).__init__()

        # self.id_container = dict.fromkeys(list_events, Category())
        self.id_container = {event: Category() for event in list_events}


    def get_tags(self, id):

        tags = self.id_container[id]
        return tags

def get_event_id_from_filename(filename):
    """ this function returns the event_id of a given filename
    param filename:: string
    """
    # assuming the event_id is in the last possible position before file type
    # ending
    event_id = filename[-14:-6]
    return event_id



class TagDataframe(object):
    """docstring for TagDataframe."""

    def __init__(self, categories=["event_id"]):
        super(TagDataframe, self).__init__()
        self.categories= categories

        self.df = pd.DataFrame(columns = categories )

        self.indexcategory= categories[0]

        self.df = self.df.set_index(self.indexcategory)

    def get_event_id_from_folder(self, folder):
        """ fill the dataframe with event_ids from the folder
        """
        files = listdir(folder)
        print("Reading Event-IDs from the folder:")
        for file in tqdm(files):
            event_id = get_event_id_from_filename(file)
            self.df = self.df.append(
                {"event_id": event_id}, ignore_index = True)
            # print("what")
        self.df = self.df.set_index("event_id")

    def printout(self):
        print(self.df.head())

    def get_row_from_id(self, event_id):
        selection = self.df.loc[event_id]
        return selection

    def get_dict_from_id(self, event_id):
        selection = self.df.loc[event_id]
        selection_dict = selection.to_dict()
        selection_dict["event_id"] = event_id
        return selection_dict

    def set_value_in_category(self, event_id, category, value):
        """ set a value in the dataframe column category
        """
        # index = self.df[self.df['event_id'] == event_id].index
        self.df.at[event_id, category] = value

    def write_to_file(self, filename):
        """ method that writes the dataframe to a file"""
        self.df.to_pickle(filename)

    def get_event_id_from_rownumber(self,rownumber):
        """ returns the event_id at the row index rownumber
        """
        return self.df.index[rownumber]


    def load_from_file(self, filename):
        """ method that loads the dataframe from a file
        """
        # TODO: check if event_id is stored as index
        frame = pd.read_pickle(filename)
        if "event_id" == frame.index.name:
            print("Index: event_id loaded successfully")
        elif "event_id" in frame.columns:
            print("Loading file.. changing index to event_id column")
            frame = frame.set_index("event_id")
        self.df = frame



class CategoryGUIFrame(ttk.LabelFrame):
    """docstring for CategoryGUIFrame."""

    def __init__(self, parent, categories=[], index_variable="event_id",
        **kwargs):
        super(CategoryGUIFrame, self).__init__(parent, **kwargs)
        self.configure(text="Category")

        self.index_variable = index_variable

        self.savebutton = ttk.Button(self, text="Save", command=
            self.__datasave)
        self.loadbutton = ttk.Button(self, text="Load", command=
            self.__dataload)

        self.savebutton.grid(row=0, column=1)
        self.loadbutton.grid(row=0, column=0)

        self.categories = categories

        self.data = TagDataframe()
        self.__print_categories()

        self.__initialize_labels()
        # print(self.labels)
        # self.__change_labels()
        # self.__initialize_labels()

        self.active_category_index=0
        if self.categories[self.active_category_index] == self.index_variable:
            self.active_category_index += 1
        # set the initial label highlight at top position
        key = self.__get_current_category()
        self.__set_active_category(key)

        # the current_item gives the rownumber or item index of the currently
        # loaded item in the dataframe
        self.current_item = 0

    def __change_labels(self):
        for key in self.labels:
            label = self.labels[key]
            label.configure(text="change")

    def __initialize_labels(self):
        # call destroy label command for existing labels?
        """
        initialize two labels with corresponding stringvars as well as proper
        dictionary information to store them for each category
        """
        self.labels = {}
        self.values = {}
        self.value_label= {}
        self.category_order = []
        row = 1
        for item in self.categories:
            label = ttk.Label(self, text=str(item))
            value_var = tk.StringVar(value="No value set")
            value = ttk.Label(self, textvariable=value_var)
            label.grid(row=row, column=0)
            value.grid(row=row,column=1)
            self.values[item] = value_var
            self.value_label[item] = value
            self.labels[item] = label
            self.category_order.append(item)
            row += 1

    def __initialize_value_dict(self):
        """ this method initializes the way how the value labels are stored"""
        pass

    def __dataload(self):
        """ method to load the attached dataframe of TagDataframe class"""
        filename = fd.askopenfilename()
        # check for if no file chosen
        if filename != ():
            self.data.load_from_file(filename)

    def __datasave(self):
        """ method to store the attached dataframe of TagDataframe class"""
        filename = fd.asksaveasfilename()
        if filename != ():
            self.data.write_to_file(filename)
            print("Saving successful.")

    def __print_categories(self):
        print(self.categories)

    def __get_current_index(self):
        # access the current index by accessing the corresponding label value
        index_value = self.values[self.index_variable]
        index_value = index_value.get()
        return index_value

    def __clear_all_highlights(self):
        """ private method to reset all the highlights for example
        via relief highlighting for all labels
        """
        for key in self.value_label:
            value = self.value_label[key]
            value.config(relief=tk.FLAT)

    def __get_current_category(self):
        active_category = self.category_order[self.active_category_index]
        return active_category

    def __set_active_category(self, category):
        active_label = self.value_label[category]
        # change the relief option of the active label
        active_label.config(relief=tk.RAISED)

    # def __update_category_display(self):
    #     """ method that updates the currently displayed category values
    #     """
    #     # todo get current event_id
    #     current_event_id = ""
    #     new_data = self.data.get_dict_from_id(current_event_id)
    #     self.categorygui.load_category_data(new_data)

    def switch_to_next_item(self):
        self.current_item += 1
        self.load_item_from_index_number(self.current_item)

    def switch_to_previous_item(self):
        self.current_item -= 1
        self.load_item_from_index_number(self.current_item)

    def load_item_from_index_number(self, index_number):
        """ this method loads the data from the given index, which is usually
        the event_id category """
        event_id = self.data.get_event_id_from_rownumber(index_number)
        new_data = self.data.get_dict_from_id(event_id)
        self.load_category_data(new_data)

    def switch_to_event(self, event_id):
        """ this method switches to the data for a given event:
        param event_id:: string """
        new_data = self.data.get_dict_from_id(event_id)
        self.load_category_data(new_data)


    def change_active_category(self):
        # reset the highlights
        self.__clear_all_highlights()
        self.active_category_index += 1
        # try-except block for catching index error when out of bounds
        try:
            active_category = self.__get_current_category()
        except IndexError:
            self.active_category_index = 0
            active_category = self.__get_current_category()
        self.__set_active_category(active_category)
        if active_category == self.index_variable:
            self.change_active_category()


    def make_category_bold(self):
        """ change the appearance of the chosen category
        """
        category = "event_id"
        value_category = self.value_label[category]
        value_category.config(relief=tk.RAISED)

    def set_value(self, option, value):
        """
        """
        self.values[option].set(value)
        current_index = self.__get_current_index()
        # print(f"current_index is {current_index}")
        self.data.set_value_in_category(current_index, option, value)
        # self.__update_category_display()

    def set_active_value(self, value):
        """ this method sets the active category to a specified value"""
        category = self.category_order[self.active_category_index]
        self.set_value(category, value)
        # self.__update_category_display()


    def load_category_data(self, data ):
        """ load data from the data dictionary
        param data:: dict"""
        for key in data:
            new_value = data[key]
            textvar = self.values[key]
            textvar.set(new_value)
