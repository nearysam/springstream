"""Main module."""

import ipyleaflet
from ipyleaflet import basemaps
import ipywidgets as widgets

class Map(ipyleaflet.Map):
    """This is a map class that is inherited from ipyleaflet

    Args:
        ipyleaflet (Map): ipyleaflet.Map class
    """    
    def __init__(self,center = [35.96, -83.46], zoom = 10, **kwargs):
        super().__init__(center = center, zoom = zoom,**kwargs)
        self.add_control(ipyleaflet.LayersControl())
    """Initialize the map.

        Args:
            center (list, optional): Set the center of the map. Defaults to [35.96, -83.46], Knoxville Long and Lat.
            zoom (int, optional): Set zoom level of the map. Defaults to 10.
        """
    def add_tile_layer(self, url, name, **kwargs):
        """Adds Tile layer

        Args:
            url (http): http supported url type
            name (tile layer name): names inherited from ipyleaflet
        """        
        layer = ipyleaflet.TileLayer(url=url, name=name, **kwargs)
        self.add(layer)
    
    def add_layers_control(self, position="topright"):
        """Adds Layers control to map class

        Args:
            position (str, optional): Allows position of controls to be modified. Defaults to "topright".
        """        
        self.add_control(ipyleaflet.LayersControl(position=position))
    
    def add_basemap(self, name):
        """Adds basemap to the current map. Defaults to Esri.WorldImagery Map.

        Args:
            name (str or object): The name of the basemap as a string, or an object representing the basemap.

        Raises:
            TypeError: If the name is neither a string nor an object representing a basemap.

        Returns:
            None
        """
        if isinstance(name, str):
            url = eval(f"basemaps.{name}").build_url()
            self.add_tile_layer(url,name)
        else:
            self.add(name)
    
    def add_geojson(self, data, name = "geojson", **kwargs):
        """Adds geojson layer to current map. Defaults to US County vector data

        Args:
            data (geojson): The data can be entered as string or dictionary
            name (str, optional): Layer name. Defaults to "us_counties_geojson".
        """        
        import json 
       
        if isinstance(data, str):
            with open(data) as f:
                data = json.load(f)
        layer = ipyleaflet.GeoJSON(data=data, name=name, **kwargs)
        self.add(layer)
    
    def add_shp(self, data, name="shp", **kwargs):
        """Adds a shapefile to the current map.

        Args:
            data (str or dict): The path to the shapefile as a string, or a dictionary representing the shapefile.
            name (str, optional): The name of the layer. Defaults to "us_counties.shp".
            **kwargs: Arbitrary keyword arguments.

        Raises:
            TypeError: If the data is neither a string nor a dictionary representing a shapefile.

        Returns:
            None
        """
        import shapefile
        import json

        if isinstance(data, str):
            with shapefile.Reader(data) as shp:
                data = shp.__geo_interface__

        self.add_geojson(data, name, **kwargs)

    def add_image(self, url, bounds, name = "image", **kwargs):
        """Adds an image overlay to OpenStreetMap map

        Args:
            url (str): URL for image
            bounds (list): Upper right and lower left bounds of image
            name (str, optional): Name of image. Defaults to "image".
        """       
        layer = ipyleaflet.ImageOverlay(url=url, bounds=bounds, name=name, **kwargs)
        self.add(layer)
    
    def add_raster(self, data, name="raster", zoom_to_layer=True, **kwargs):
        """Adds raster layer to map.

        Args:
            data (str): The file path to raster data.
            name (str, optional): Name of layer. Defaults to "raster".
        """

        try:
            from localtileserver import TileClient, get_leaflet_tile_layer
        except ImportError:
            raise ImportError("Must install 'localtileserver' package.")

        client = TileClient(data)
        layer = get_leaflet_tile_layer(client, name=name, **kwargs)
        self.add(layer)

        if zoom_to_layer:
            self.center = client.center()
            self.zoom = client.default_zoom
    
    def add_zoom_slider(
        self, description="Zoom level", min=0, max=24, value=10, position="topright"
    ):
        """Adds a slider to map.

        Args:
            position (str, optional): The position of slider. Defaults to "topright".
        """
        zoom_slider = widgets.IntSlider(
            description=description, min=min, max=max, value=value
        )

        control = ipyleaflet.WidgetControl(widget=zoom_slider, position=position)
        self.add(control)
        widgets.jslink((zoom_slider, "value"), (self, "zoom"))
    
    def add_widget(self, widget, position="topright"):
        """Adds a widget, imported from ipywidgets.

        Args:
            widget (object): Widget that you want added.
            position (str, optional): Position of widget. Defaults to "topright".
        """
        control = ipyleaflet.WidgetControl(widget=widget, position=position)
        self.add(control)
    
    def add_basemap_gui(self, basemaps=None, position="topright"):
        """Adds GUI to map. Includes basemap options under 'basemap selector'

        Args:
            position (str, optional): Position of GUI. Defaults to "topright".
        """

        basemap_selector = widgets.Dropdown(
            options=[
                "OpenStreetMap",
                "OpenTopoMap",
                "Esri.WorldImagery",
                "Esri.NatGeoWorldMap",
                "CartoDB.DarkMatter"
            ],
            description="Basemap",
        )

        def update_basemap(change):
            self.add_basemap(change["new"])

        basemap_selector.observe(update_basemap, "value")

        control = ipyleaflet.WidgetControl(widget=basemap_selector, position=position)
        self.add(control)