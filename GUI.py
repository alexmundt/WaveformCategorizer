import tkinter as tk
from tkinter import ttk
import os
from obspy import read
from tqdm import tqdm
from config import Configuration
from Categories import TagDataframe, CategoryGUIFrame
import scipy.fft

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np

class LabelFrame(ttk.Frame):
    """docstring for LabelFrame.
    db_description is a one-word description of the database"""
    def __init__(self, parent, db_description, **kwargs):
        super(LabelFrame, self).__init__(parent, **kwargs)
        # append white space for db_description if it does not have one already
        if db_description[-1] != " ":
            db_description += " "
        # what happens if db_description is an empty string?

        self.current_filename_display = tk.StringVar()

        database_label = ttk.Label(self,
            text=f"{db_description}")
        current_database_label = ttk.Label(self, textvariable =
            self.current_filename_display)

        database_label.grid(column = 0, row = 0, padx = 10, pady= 10)
        current_database_label.grid(column=1, row=0, padx = 10, pady= 10)

    def set_filename(self, name):
        reduced_name = os.path.basename(name)
        self.current_filename_display.set(reduced_name)

class FreqEntry(ttk.Frame):
    """docstring for FreqEntry.
    This class is used to combine Entry and label for manual frequency input  """
    def __init__(self, parent, title, **kwargs):
        super(FreqEntry, self).__init__(parent, **kwargs)
        self.title = title

        self.EntryVar = tk.StringVar()

        self.label = ttk.Label(self, text = f"{title}")
        self.Entry = ttk.Entry(self, textvariable=self.EntryVar)

        self.label.grid(row=0, column=0)
        self.Entry.grid(row=0, column=1)
        self.grid()

    def get_value(self):
        """ return the value in the Entry """
        value = self.EntryVar.get()
        return value

    def set_value(self, value):
        """ set the value in the Entry variable"""
        stringvalue = str(value)
        self.EntryVar.set(stringvalue)

class IntEntry(ttk.Frame):
    """docstring for IntEntry.
    This class is used to combine Entry and label for manual input of integer
    only values """
    def __init__(self, parent, title, **kwargs):
        super(IntEntry, self).__init__(parent, **kwargs)
        self.title = title

        self.EntryVar = tk.StringVar()

        self.label = ttk.Label(self, text = f"{title}")
        self.Entry = ttk.Entry(self, textvariable=self.EntryVar)

        self.label.grid(row=0, column=0)
        self.Entry.grid(row=0, column=1)
        self.grid()

    def get_value(self):
        """ return the value in the Entry """
        value = int(self.EntryVar.get())
        return value

    def set_value(self, value):
        """ set the value in the Entry variable"""
        stringvalue = str(value)
        self.EntryVar.set(stringvalue)

class FileIndexCounter(tk.Label):
    """docstring forFileIndexCounter.
    This Class describes a Label for the current file index.
    It is created with a folder variable which is
    the folder containing the files to be indexed"""

    def __init__(self, parent, folder, **kwargs):
        super(FileIndexCounter, self).__init__(parent, **kwargs)

        files = os.listdir(folder)
        self.num_files = len(files)

        self.folder = folder
        self.configure(text=f"Files {self.num_files}")
        self.grid()

        self.set_index(0)

    def update(self):
        self.configure(text=f"File {self.index} of {self.num_files}")

    def set_index(self, index):
        self.index = index


class MainFrame(ttk.Frame):
    """docstring for MainFrame."""

    def __init__(self, *args, **kwargs):
        try:
            self.folder = kwargs.pop("folder")
        except:
            self.folder = "example_data"
            print("Using default folder 'example data'.")
        try:
            self.max_freq = kwargs.pop("max_freq")
        except:
            self.max_freq = 0.5
            print("Using maximum frequency of 0.5Hz for plotting.")


        super(MainFrame, self).__init__(*args, **kwargs)
        # self.arg = arg


        self.infoframe = ttk.Frame(self)

        self.filelabel = LabelFrame(self.infoframe, "Current File")

        self.filelabel.grid()



        self.fileindexcounter = FileIndexCounter(self.infoframe,
            self.folder)

        self.__create_data()
        self.__create_figure()

        self.lowfreqentry = FreqEntry(self.infoframe,
            "Lowpass Frequency")
        self.highfreqentry = FreqEntry(self.infoframe,
            "Highpass Frequency")

        self.orderEntry = IntEntry(self.infoframe, "Filter order: ")

        # set the filename
        self.configfile = "config.ini"
        self.__load_config(filename=self.configfile)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=0, row=0, rowspan=5)

        self.button_frame = ttk.Frame(self)

        next_button = tk.Button(self.button_frame, text="Next Plot", command=
            self.__next_figure )
        prev_button = tk.Button(self.button_frame, text="Previous Plot", command=
            self.__prev_figure)
        next_button.grid(row = 0, column = 2)
        prev_button.grid(row = 0, column = 0)

        # lose focus button for key press mode
        keyboard_mode_button = tk.Button(self.button_frame,
            text="Keyboard navigation mode",
            command = self.__losefocus)
        keyboard_mode_button.grid(row = 0, column = 1)

        # filter Button
        filter_button = tk.Button(self.button_frame, text="Filter", command=
            self.__filter_button)
        filter_button.grid(row=1, column=0)

        # reset filter button
        reset_filter_button = tk.Button(self.button_frame, text="Reset Filter",
            command = self.__reset_filter)
        reset_filter_button.grid(row=1, column=1)

        self.button_frame.grid(row=1, column=1)

        self.progress_variable = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(self, orient="horizontal", mode=
            "determinate", variable = self.progress_variable)
        self.progressbar.grid()

        self.progressbar["value"] = 10
        self.index = -1

        # self.dataloader = DataLoader()
        data_folder = self.folder
        self.dataset = DataSet()
        self.dataset.generate_random_set(100)
        self.dataset.read_folder(data_folder)
        self.dataset.calculate_spectra()
        # print(x)

        # load the category GUI
        categories = ["event_id", "noise", "quality"]
        self.categorygui = CategoryGUIFrame(self, categories=categories)
        self.categorygui.grid(column=1, row=3)
        self.categorygui.data.get_event_id_from_folder(data_folder)
        # self.tagdata = TagDataframe(categories = categories)
        # self.tagdata.get_event_id_from_folder(data_folder)

        self.bind("<Key>", self.keypress_event )

        self.infoframe.grid(column=1, row=0)
        self.grid()

    def __load_config(self, filename):
        """ load the config values into the stringvars of the entrys
        """
        config = Configuration(filename=filename)
        self.config = config
        # get the values from the loaded config
        lowfreq = config.get_option_value("lowpass")
        highfreq = config.get_option_value("highpass")
        order = config.get_option_value("order")
        # set the values of the entries to the values from the config file
        self.lowfreqentry.set_value(lowfreq)
        self.highfreqentry.set_value(highfreq)
        self.orderEntry.set_value(order)

    def __update_config(self):
        """ this method is called when the config file is updated
        """
        lowfreq = self.lowfreqentry.get_value()
        highfreq = self.highfreqentry.get_value()
        order = self.orderEntry.get_value()
        self.config.set_value("order", order)
        self.config.set_value("highpass", highfreq)
        self.config.set_value("lowpass", lowfreq)
        self.config.write_to_file()


    def __losefocus(self):
        self.focus_set()

    def keypress_event(self, event):
        # print(event)
        # self.__update_figure()
        # try:
        #     if event.keysym == "Left":
        #         print("heyyya")
        # except Exception as ex:
        #     print("Error during keysym?")
        #     print(ex)
        if event.keysym == "Left":
            self.__prev_figure()

        elif event.keysym == "Right":
            self.__next_figure()
        elif event.keysym in ["1","2","3","4","5"]:
            new_value = event.keysym
            self.categorygui.set_active_value(new_value)
            # self.tagdata.set_value_in_category(self.event_id,
            #     "noise", new_value)
            # self.__update_tags()
        elif event.keysym == "q":
            self.categorygui.change_active_category()

    def __update_progress(self, value):
        # self.progressbar["value"] = value*100
        # print(f"value at {value}")
        self.progress_variable.set(value)
        self.update_idletasks()

    def __create_data(self):
        self.t = np.arange(0, 3, .01)
        self.y = 2. * np.sin(2. * np.pi * self.t)

    def __create_figure(self):
        self.fig = Figure(figsize = [10, 7.5])
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)
        # self.ax.plot(self.y)

    def __next_figure(self):
        self.index += 1
        self.__update_figure()
        self.__update_event_id()
        self.categorygui.switch_to_event(self.dataset.event_ids[self.index])
        # self.categorygui.switch_to_next_item()
        # self.__update_tags()

    def __prev_figure(self):
        self.index -= 1
        self.__update_figure()
        self.__update_event_id()
        self.categorygui.switch_to_event(self.dataset.event_ids[self.index])
        # self.categorygui.switch_to_previous_item()
        # self.__update_tags()

    def __update_event_id(self):
        self.event_id = self.filename[-14:-6]

    # def __update_tags(self):
    #     #TODO: get dict with tags from tag frame
    #     new_data = self.tagdata.get_dict_from_id(self.event_id)
    #     self.categorygui.load_category_data(new_data)


    def __filter_button(self):
        # TODO load frequency values from entries
        lowfreq = float(self.lowfreqentry.get_value())
        highfreq = float(self.highfreqentry.get_value())
        order = self.orderEntry.get_value()
        self.dataset.filter(lowfreq, highfreq, order, progress =
            self.__update_progress)
        self.__update_figure()
        self.__update_config()

    def __reset_filter(self):
        self.dataset.reset_filter()
        self.__update_figure()

    def __update_figure(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        # do not allow negative indexes for scrolling
        if self.index < 0:
            self.index = 0
        try:
            x,y = self.dataset[self.index]
            freq, fft = self.dataset.spectra[self.index]
            filtered_x,filtered_y = self.dataset.filtered_data_set[self.index]
            filtered_freq, filtered_fft = self.dataset.filtered_spectra[
                self.index]
        except IndexError:
            self.index = 0
            x,y = self.dataset[self.index]
            freq, fft = self.dataset.spectra[self.index]
            filtered_x,filtered_y = self.dataset.filtered_data_set[self.index]
            filtered_freq, filtered_fft = self.dataset.filtered_spectra[
                self.index]

        self.ax1.plot(x,y)
        self.ax2.plot(freq,np.abs(fft))
        self.ax2.set_xlim([0,self.max_freq])
        self.ax3.plot(filtered_x, filtered_y)
        self.ax4.plot(filtered_freq, np.abs(filtered_fft))
        self.ax4.set_xlim([0,self.max_freq])

        self.canvas.draw()
        self.filename = self.dataset.filenames[self.index]
        self.filelabel.set_filename(str(self.filename))
        self.fileindexcounter.set_index(self.index+1)
        self.fileindexcounter.update()


class DataLoader(object):
    """docstring for DataLoader."""

    def __init__(self, filename=None):
        super(DataLoader, self).__init__()
        self.filename = filename

    def __generate_data(self):
        x = np.linspace(0,100,100)
        y= np.random.rand(100)+np.sin(x)
        return x,y

    def load_data(self):
        x,y = self.__generate_data()
        return x,y

class DataGenerator(object):
    """docstring for DataGenerator."""

    def __init__(self, num_data):
        super(DataGenerator, self).__init__()
        self.num_data = num_data
        self.data_points = 100

    def __generate_data(self):
        x = np.linspace(0,self.data_points,self.data_points)
        y= np.random.rand(self.data_points)+np.sin(x)
        return x,y

    def generate_set(self, num_data = 0):
        if num_data == 0:
            num_data = self.num_data
        data_set = []
        for i in range(num_data):
            x,y = self.__generate_data()
            data_set.append( [x,y] )

        return data_set

class DataSet(object):
    """docstring for DataSet."""

    def __init__(self):
        super(DataSet, self).__init__()

        self.data_points = 100

    def __generate_data(self):
        """ this method generates a random x,y data set
        """
        x = np.linspace(0,self.data_points,self.data_points)
        y= np.random.rand(self.data_points)+np.sin(x)
        return x,y

    def generate_random_set(self, num_data):
        """ this method generates a set of x,y dataset pairs
        """
        data_set = []
        for i in range(num_data):
            x,y = self.__generate_data()
            data_set.append( [x,y] )

        self.data_set = data_set

    def __getitem__(self, i):
        return self.data_set[i]

    def read_folder(self, folder):
        """TODO: this method reads a folder"""
        files = os.listdir(folder)
        data_set = []
        filenames = []
        streams = []
        event_ids = []
        print("Reading files...")
        for file in tqdm(files):
            event_id = file[-14:-6]
            filenames.append(file)
            filename = folder + "/" + file
            st = read(filename)
            tr = st[0]
            x,y = tr.times("matplotlib"), tr.data
            streams.append(st)
            data_set.append([x,y])
            event_ids.append(event_id)
        self.event_ids = event_ids
        self.data_set = data_set
        self.filtered_data_set = data_set
        self.filenames = filenames
        self.streams = streams

    def filter(self, lowfreq, highfreq, order = 4, progress = None):
        """ filter the stored streams and recreate the dataset
        """
        data_set = []
        spectra = []
        # initialize variables for counting the progress
        progress_counter = 0
        number_streams = len(self.streams)
        for st in self.streams:
            filter_st = st.copy()
            filter_st.filter("lowpass", freq = lowfreq, corners = order)
            filter_st.filter("highpass", freq = highfreq,corners = order)
            tr = filter_st[0]
            x,y = tr.times("matplotlib"), tr.data
            time_for_fft = tr.times("relative")
            data_set.append([x,y])
            # calculate spectra for the filtered datasets
            n_samples = len(time_for_fft)
            dt = time_for_fft[1]-time_for_fft[0]
            freq = scipy.fft.rfftfreq(n_samples, dt)
            fft = scipy.fft.rfft(y)
            spectra.append([freq, fft])
            progress_counter += 1
            if progress != None:
                value = float(progress_counter/number_streams)*100
                # pass the current status to the progress
                progress(value)
        self.filtered_spectra = spectra
        self.filtered_data_set = data_set

    def reset_filter(self):
        data_set = []
        for st in self.streams:
            tr = st[0]
            x,y = tr.times("matplotlib"), tr.data
            data_set.append([x,y])
        self.data_set = data_set

    def calculate_spectra(self):
        """ this method calculates the Fourier spectra of each dataset and
        stores it in the bound attribute self.spectra
        """
        spectra = []
        for st in self.streams:
            tr = st[0]
            time,values = tr.times("relative"), tr.data
            n_samples = len(time)
            dt = time[1]-time[0]
            freq = scipy.fft.rfftfreq(n_samples, dt)
            fft = scipy.fft.rfft(values)
            spectra.append([freq, fft])
        self.spectra = spectra
        self.filtered_spectra = spectra
