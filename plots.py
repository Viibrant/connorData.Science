from bokeh.plotting import figure
from bokeh.models import (DataRange1d, WheelZoomTool, HoverTool, DatetimeTickFormatter,
                          NumeralTickFormatter, ColumnDataSource, GeoJSONDataSource, LinearColorMapper, ColorBar)
from bokeh.palettes import brewer

from check_file import get_dataset
import pandas as pd
import geopandas as gpd


class covid:

    def __init__(self, endpoint):
        raw_data = get_dataset(endpoint)
        self.statistics = raw_data
        self.statistics['date'] = pd.to_datetime(self.statistics['date'])
        # self.statistics.sort_values("date", ascending=False)

        # convert all dates to standard format
        self.latest_date = self.statistics.iloc[0]['date'].strftime("%Y-%m-%d")

        # Create another dataframe, containing statistics only for latest date & geographical data
        shp = gpd.read_file(
            "shape/Counties_and_Unitary_Authorities__December_2017___EW_BGC.shp")
        shp.rename(columns={"CTYUA17CD": "areaCode",
                            "CTYUA17NM": "areaName"}, inplace=True)

        ldf = raw_data.loc[raw_data['date'] == raw_data.iloc[0]["date"]]

        self.ldf = gpd.GeoDataFrame(
            ldf.merge(shp, left_on="areaName", right_on="areaName"))

    def get_newcases_nationally(self):
        # group all records with same dates together, then create a new dataframe and apply sum to all other columns
        grouped_dates = self.statistics.groupby("date").newCasesBySpecimenDate
        aggregated = pd.concat([grouped_dates.apply(
            sum), grouped_dates.count()], axis=1, keys=["date"])
        # The dates column changed to row names so take all names and cast to list
        return {"dates": list(aggregated.index), "cases": aggregated["date"].to_list()}

    def get_newvaccinations_nationally(self):
        grouped_dates = self.statistics.groupby(
            "date").newPeopleVaccinatedCompleteByVaccinationDate
        aggregated = pd.concat([grouped_dates.apply(
            sum), grouped_dates.count()], axis=1, keys=["date"])
        # The dates column changed to row names so take all names and cast to list
        return {"dates": list(aggregated.index), "cases": aggregated["date"].to_list()}

    def cases_graph(self):
        # Generate graph for New Cases vs Date
        source = ColumnDataSource(data=self.get_newcases_nationally())
        p = figure(
            title="New Covid Cases as of %s" % self.latest_date,
            tools="pan, reset",
            toolbar_location=None,
            sizing_mode="stretch_both",
            plot_height=500,
            x_axis_type="datetime",
            x_range=DataRange1d(bounds="auto"),
            y_range=DataRange1d(bounds="auto")
        )

        zoom_tool = WheelZoomTool()
        zoom_tool.maintain_focus = False

        hover_tool = HoverTool()
        hover_tool.mode = "vline"
        hover_tool.tooltips = [
            ("Selected Date", "@dates{%d %b %Y}"), ("New Cases", "@cases{0,0}")]
        hover_tool.formatters = {"@dates": "datetime", "@cases": "numeral"}

        p.add_tools(zoom_tool, hover_tool)
        p.toolbar.active_scroll = p.select_one(WheelZoomTool)

        date_format = "%d %b %Y"
        p.xaxis.formatter = DatetimeTickFormatter(
            hours=date_format,
            days=date_format,
            months=date_format,
            years=date_format
        )
        p.xaxis.axis_label = "Date"

        p.yaxis.formatter = NumeralTickFormatter(format="0,0")
        p.yaxis.axis_label = "New Cases"
        p.line(x="dates", y="cases", source=source, color='red')

        return p

    def vaccines_graph(self):
        source = ColumnDataSource(data=self.get_newvaccinations_nationally())
        p = figure(
            title="People fully vaccinated as of %s" % self.latest_date,
            tools="pan, reset",
            toolbar_location=None,
            sizing_mode="stretch_both",
            plot_height=500,
            x_axis_type="datetime",
            x_range=DataRange1d(bounds="auto"),
            y_axis_location="right",
            y_range=DataRange1d(bounds="auto")
        )

        zoom_tool = WheelZoomTool()
        zoom_tool.maintain_focus = False

        hover_tool = HoverTool()
        hover_tool.mode = "vline"
        hover_tool.tooltips = [
            ("Selected Date", "@dates{%d %b %Y}"), ("Newly Fully Vaccinated", "@cases{0,0}")]
        hover_tool.formatters = {"@dates": "datetime", "@cases": "numeral"}

        p.add_tools(zoom_tool, hover_tool)
        p.toolbar.active_scroll = p.select_one(WheelZoomTool)

        date_format = "%d %b %Y"
        p.xaxis.formatter = DatetimeTickFormatter(
            hours=date_format,
            days=date_format,
            months=date_format,
            years=date_format
        )
        p.xaxis.axis_label = "Date"

        p.yaxis.formatter = NumeralTickFormatter(format="0,0")
        p.yaxis.axis_label = "People Fully Vaccinated"
        p.line(x="dates", y="cases", source=source, color='blue')

        return p

    def cases_map(self):
        geosource = GeoJSONDataSource(
            geojson=self.ldf.to_json(default=lambda time: time.__str__()))
        highest_cases = self.ldf.sort_values(

            "newCasesBySpecimenDate", ascending=False).iloc[0]["newCasesBySpecimenDate"]
        palette = brewer['YlOrRd'][9][::-1]

        colour_mapper = LinearColorMapper(
            palette=palette, low=0, high=highest_cases)
        colour_bar = ColorBar(color_mapper=colour_mapper,
					border_line_color=None,
					location=(0, 0),
					orientation="horizontal")

        p = figure(toolbar_location='below', title="New Coronavirus Cases per Area", x_range=DataRange1d(bounds="auto"),
					y_range=DataRange1d(bounds="auto"), tools="pan, reset"
				)

        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        p.axis.visible = False
        county = p.patches('xs', 'ys', 
						source=geosource,
						fill_color={"field": "newCasesBySpecimenDate",
									"transform": colour_mapper},
						line_color="grey",
						line_width=0.25,
						fill_alpha=1)

        p.add_tools(
            HoverTool(
                renderers=[county],
                tooltips=[
                    ('Area', '@areaName'),
                    ('New Cases',
					'@{column}'.format(column="newCasesBySpecimenDate"))
                ]),
            WheelZoomTool(maintain_focus=False))
        p.toolbar.active_scroll = p.select_one(WheelZoomTool)
        p.add_layout(colour_bar, "below")

        return p

    def vaccines_map(self):
        geosource = GeoJSONDataSource(
            geojson=self.ldf.to_json(default=lambda time: time.__str__()))
        
        highest_cases = self.ldf.sort_values(
            "newPeopleVaccinatedCompleteByVaccinationDate", ascending=False).iloc[0]["newPeopleVaccinatedCompleteByVaccinationDate"]
        palette = brewer['YlOrRd'][9][::-1]

        colour_mapper = LinearColorMapper(
            palette=palette, low=0, high=highest_cases)
        colour_bar = ColorBar(color_mapper=colour_mapper,
					border_line_color=None,
					location=(0, 0),
					orientation="horizontal")

        p = figure(toolbar_location='below', title="New people fully vaccinated", x_range=DataRange1d(bounds="auto"),
					y_range=DataRange1d(bounds="auto"), tools="pan, reset"
				)

        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        p.axis.visible = False
        county = p.patches('xs', 'ys', 
						source=geosource,
						fill_color={"field": "newPeopleVaccinatedCompleteByVaccinationDate",
									"transform": colour_mapper},
						line_color="grey",
						line_width=0.25,
						fill_alpha=1)

        p.add_tools(
            HoverTool(
                renderers=[county],
                tooltips=[
                    ('Area', '@areaName'),
                    ('New Cases',
					'@{column}'.format(column="newPeopleVaccinatedCompleteByVaccinationDate"))
                ]),
            WheelZoomTool(maintain_focus=False))
        p.toolbar.active_scroll = p.select_one(WheelZoomTool)
        p.add_layout(colour_bar, "below")

        return p