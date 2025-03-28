import importlib.resources
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ontologysim.ProductionSimulation.logger.Enum_Logger import Folder_name
from ontologysim.ProductionSimulation.utilities import Init, sanitize_path


class Plot:
    """
    runs seperately from the simulation, the goal of this plot class is to plot the log data,
    the class needs an extra plot ini
    """

    def __init__(self, log_dir, config_path):
        config_path = sanitize_path(os.getcwd(), config_path)
        # Read from Configuration File
        plot_conf = Init(config_path)
        plot_conf.read_ini_file()

        self.file_type_list = plot_conf.configs["Log"]["file_type"]

        self.log_dir = log_dir
        save_dir = plot_conf.configs["Log"]["save_dir"]

        save_dir = sanitize_path(os.getcwd(), log_dir / save_dir)
        save_dir.mkdir(exist_ok=True)

        self.save_dir = save_dir

        self.color_qualitative = plot_conf.configs["Style"]["colormap"]
        self.marker = plot_conf.configs["Style"]["marker"]

        self.end_file_name = "_logger.csv"

        self.line_plot = plot_conf.configs["LinePlot"]["y_data"]
        self.multiple_line_plot = plot_conf.configs["MultipleLinePlot"]["settings"]
        self.scatter_plot_x = plot_conf.configs["ScatterPlot"]["x_data"]
        self.scatter_plot_y = plot_conf.configs["ScatterPlot"]["y_data"]

        colormap  = matplotlib.colormaps.get(self.color_qualitative)
        if colormap is None:
            self.colorMap = self.color_qualitative
        else:
            self.colorMap = colormap.colors

        # look up file to get information about the type (percentage, number..) of the kpi
        with importlib.resources.path("ontologysim.ProductionSimulation.logger.plot", "y_lookup_tabel.ini") as axis_config_path:
            # Read from Configuration File
            axis_conf = Init(axis_config_path)
            axis_conf.read_ini_file()
            self.number_kpis = axis_conf.configs["LookUp"]["number"]
            self.time_kpis = axis_conf.configs["LookUp"]["time"]
            self.percentage_kpis = axis_conf.configs["LookUp"]["percentage"]

    def plot(self):
        """
        main method for plotting, distributes the tasks, different plot tpyes
        """
        if len(self.line_plot) > 0:
            self.plot_line()

        if len(self.multiple_line_plot) > 0:
            self.plot_multiple_line()

        if len(self.scatter_plot_x) > 0 and len(self.scatter_plot_x) == len(
            self.scatter_plot_y
        ):
            self.plot_scatter()

    def plot_line(self):
        """
        plotting the kpi over time in a line chart
        """
        for setting_dict in self.line_plot:
            fig, ax = plt.subplots()
            x = self.read_log("time", setting_dict["type"], "all")
            self.adaptLine(setting_dict, x, ax)

            ax.set(
                ylabel=self.setYLabel(setting_dict["kpi"]),
                xlabel="time (s)",
                title=setting_dict["kpi"] + " " + setting_dict["type"],
            )
            ax.grid()

            if self.save_dir != "":
                for file_type in self.file_type_list:
                    filename = "line_plot_{kpi}_{typ}.{ext}".format(kpi=setting_dict["kpi"], typ=setting_dict["type"], ext=file_type)
                    fig.savefig(
                        sanitize_path(os.getcwd(), self.save_dir / filename),
                        format=file_type,
                    )
            plt.show()

    def setYLabel(self, kpi):
        """
        set the kpi y aches

        :param kpi: str
        :return: str: type
        """
        if kpi in self.percentage_kpis:
            return "percentage (%)"
        elif kpi in self.time_kpis:
            return "time (s)"
        elif kpi in self.number_kpis:
            return "number"

    def read_log(self, kpi, type, object_name):
        """
        transforms the csv to a pandas and only returns the suitalbe column

        :param kpi: str
        :param type: str
        :param object_name: str, e.g. m_0
        :return:
        """
        path = sanitize_path(os.getcwd(), self.adaptLogPath(type) / f"{object_name}_logger.csv")

        data = pd.read_csv(path, sep=";")

        return data[kpi]

    def adaptLogPath(self, type):
        """
        the time analyse plots are lying in subfolder, therefore the subfolders were added to the path

        :param type:
        :return:
        """
        if type == "machine":
            path = sanitize_path(os.getcwd(), self.log_dir / Folder_name.machine.value)
        elif type == "queue":
            path = sanitize_path(os.getcwd(), self.log_dir / Folder_name.queue.value)
        elif type == "transporter":
            path = sanitize_path(os.getcwd(), self.log_dir / Folder_name.transporter.value)
        elif type == "sim":
            path = sanitize_path(os.getcwd(), self.log_dir / Folder_name.sim.value)
        elif type == "transporter_distribution":
            path = sanitize_path(os.getcwd(), self.log_dir / Folder_name.transporter_distribution.value)
        elif type == "product":
            path = sanitize_path(os.getcwd(), self.log_dir / Folder_name.product.value)
        else:
            raise Exception(type + " not defined")
        return path

    def plot_multiple_line(self):
        """
        allowes to plot multiple kpi's in one chart, currently restricted to 3 kpi's
        each chart is plotted in a sub diagramm
        """
        for multi_plot in self.multiple_line_plot:
            fig, axs = plt.subplots(len(multi_plot["data"]), 1)

            ax0 = None
            i = 0
            if len(multi_plot["data"]) > 3:
                raise Exception("to many diagramms")
            for setting_dict in multi_plot["data"]:
                x = self.read_log("time", setting_dict["type"], "all")

                self.adaptLine(setting_dict, x, axs[i])
                axs[i].title.set_text(setting_dict["kpi"] + " " + setting_dict["type"])

                if i != len(multi_plot["data"]) - 1:
                    plt.setp(axs[0].get_xticklabels(), fontsize=6, visible=False)
                i += 1
            fig.suptitle(multi_plot["title"], fontsize=12)
            plt.xlim(min(x), max(x))
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            if self.save_dir != "":
                for file_type in self.file_type_list:
                    filename = "multiple_line_plot_{kpi}_{typ}.{ext}".format(kpi=setting_dict["kpi"], typ=setting_dict["type"], ext=file_type)
                    fig.savefig(
                        sanitize_path(os.getcwd(), self.save_dir / filename),
                        format=file_type,
                    )

            plt.show()

    def adaptLine(self, setting_dict, x, ax):
        """
        adding a line to the chart

        :param setting_dict:
        :param x-values
        :param ax: axes
        """
        i = 0
        b = 0
        object_list = []
        if "object_name" in setting_dict.keys():
            object_list = setting_dict["object_name"]

        else:
            path = sanitize_path(os.getcwd(), self.adaptLogPath(setting_dict["type"]))
            onlyfiles = [
                f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
            ]

            for file in onlyfiles:
                object_name = ""
                if self.end_file_name in file:
                    object_name = file.replace(self.end_file_name, "")
                object_list.append(object_name)

        for object_name in object_list:
            y = self.read_log(setting_dict["kpi"], setting_dict["type"], object_name)
            ax.plot(
                x, y, label=object_name, color=self.colorMap[i], marker=self.marker[b]
            )
            i += 1
            if i >= len(self.colorMap):
                i = 0
                b += 1

        ax.legend(loc=1)

    def scatter_hist(self, x, y, ax, ax_histx, ax_histy):
        """
        plottin the values in a scattered histogramm

        :param x:
        :param y:
        :param ax:
        :param ax_histx:
        :param ax_histy:
        """
        # no labels
        ax_histx.tick_params(axis="x", labelbottom=False)
        ax_histy.tick_params(axis="y", labelleft=False)

        # the scatter plot:
        ax.scatter(x, y)

        # now determine nice limits by hand:
        binwidth = 0.1
        xmax = max(x)
        xmin = min(x)
        ymax = max(y)
        ymin = min(y)

        lim_x_max = (int(xmax / binwidth) + 1) * binwidth
        lim_x_min = (int(xmin / binwidth) + 1) * binwidth

        lim_y_max = (int(ymax / binwidth) + 1) * binwidth
        lim_y_min = (int(ymin / binwidth) + 1) * binwidth

        # print(lim_min,lim_max)
        bins_x = np.arange(lim_x_min - binwidth, lim_x_max + binwidth, binwidth)
        bins_y = np.arange(lim_y_min - binwidth, lim_y_max + binwidth, binwidth)

        ax_histx.hist(x, bins=bins_x)
        ax_histy.hist(y, bins=bins_y, orientation="horizontal")

    def plot_scatter(self):
        """
        plotting a scatte plot with two histogram on each axes
        """
        left, width = 0.1, 0.65
        bottom, height = 0.1, 0.65
        spacing = 0.005

        rect_scatter = [left, bottom, width, height]
        rect_histx = [left, bottom + height + spacing, width, 0.2]
        rect_histy = [left + width + spacing, bottom, 0.2, height]

        for i in range(len(self.scatter_plot_x)):
            # start with a square Figure
            fig = plt.figure(figsize=(8, 8))

            ax = fig.add_axes(rect_scatter)
            ax_histx = fig.add_axes(rect_histx, sharex=ax)
            ax_histy = fig.add_axes(rect_histy, sharey=ax)
            setting_dict_x = self.scatter_plot_x[i]
            setting_dict_y = self.scatter_plot_y[i]
            x = self.read_log(
                setting_dict_x["kpi"],
                setting_dict_x["type"],
                setting_dict_x["object_name"],
            )
            y = self.read_log(
                setting_dict_y["kpi"],
                setting_dict_y["type"],
                setting_dict_y["object_name"],
            )

            # use the previously defined function
            self.scatter_hist(x, y, ax, ax_histx, ax_histy)
            ax.set(
                xlabel=setting_dict_x["kpi"]
                + " "
                + setting_dict_x["type"]
                + " "
                + setting_dict_x["object_name"],
                ylabel=setting_dict_y["kpi"]
                + " "
                + setting_dict_y["type"]
                + " "
                + setting_dict_y["object_name"],
            )

            title = (
                "Compare "
                + setting_dict_x["kpi"]
                + " "
                + setting_dict_x["type"]
                + " "
                + setting_dict_x["object_name"]
                + " vs "
                + setting_dict_y["kpi"]
                + " "
                + setting_dict_y["type"]
                + " "
                + setting_dict_y["object_name"]
            )
            fig.suptitle(title, fontsize=12)

            if self.save_dir != "":
                for file_type in self.file_type_list:
                    filename = "scatter_plot{x_kpi} {x_typ}_{x_obj_name}__{y_kpi}_{y_typ}_{y_obj_name}.{ext}".format(
                        x_kpi=setting_dict_x["kpi"],
                        x_typ=setting_dict_x["type"],
                        x_obj_name=setting_dict_x["object_name"],
                        y_kpi=setting_dict_y["kpi"],
                        y_typ=setting_dict_y["type"],
                        y_obj_name=setting_dict_y["object_name"],
                        ext=file_type,
                    )
                    fig.savefig(
                        sanitize_path(os.getcwd(), self.save_dir / filename),
                        format=file_type,
                    )

            plt.show()
