"""Main module."""

import folium
import geopandas as gpd
from IPython.display import display
from branca.element import Figure
import json
import requests
import io

class Map:
    """Main module for creating interactive maps using Folium."""

    def __init__(self, center=[35.52, -86.46], zoom=7):
        """Initialize the map.

        Args:
            center (list, optional): The center coordinates of the map. Defaults to [35.52, -86.46].
            zoom (int, optional): The initial zoom level of the map. Defaults to 7.
        """
        self.m = folium.Map(location=center, zoom_start=zoom)
        self.basemap = None

    def add_data_layer(self, gdf, name="Data Layer", style=None):
        """Adds a data layer to the current map.

        Args:
            gdf (GeoDataFrame): The GeoDataFrame containing the data to be added.
            name (str, optional): The name of the layer. Defaults to "Data Layer".
            style (dict, optional): The style to apply to the layer. Defaults to None.
        """
        try:
            # Convert the data to GeoJSON format
            geojson_data = gdf.to_crs(epsg='4326').to_json()

            # Define a style function
            def style_function(feature):
                return style if style else {}

            # Create a GeoJson layer with the style function
            geojson_layer = folium.GeoJson(
                geojson_data,
                name=name,
                style_function=style_function
            )

            # Add the GeoJson layer to the map
            self.m.add_child(geojson_layer)
        except Exception as e:
            print(f"Error adding data layer: {e}")

    def add_shp(self, url, name="shp", style=None, icon_url=None):
        """Adds a shapefile from a URL path to the current map.

        Args:
            url (str): The URL path to the shapefile.
            name (str, optional): The name of the layer. Defaults to "shp".
            style (dict, optional): The style to apply to the layer. Defaults to None.
            icon_url (str, optional): The URL of the custom icon for markers. Defaults to None.
        """
        try:
            # Fetch the shapefile data from the URL
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Read the shapefile using geopandas
                gdf = gpd.read_file(io.BytesIO(response.content))

                # Convert the data to GeoJSON format
                geojson_data = gdf.to_crs(epsg='4326').to_json()

                # Define a style function for the GeoJSON layer
                def style_function(feature):
                    return style if style else {}

                # Create a GeoJson layer with the style function
                geojson_layer = folium.GeoJson(
                    geojson_data,
                    name=name,
                    style_function=style_function
                )
                # Add the GeoJson layer to the map
                self.m.add_child(geojson_layer)

                # Add markers with custom icons if icon_url is provided
                if icon_url:
                    for index, row in gdf.iterrows():
                        icon = folium.features.CustomIcon(icon_url, icon_size=(20, 20))
                        folium.Marker([row.geometry.y, row.geometry.x], icon=icon, tooltip=row["name"]).add_to(self.m)

            else:
                print("Failed to fetch shapefile data from URL")
        except Exception as e:
            print(f"Error adding shapefile from URL: {e}")

    def spatial_analysis(self, url1, url2):
        """Performs spatial analysis to find intersections between two shapefiles.

        Args:
            url1 (str): The URL path to the first shapefile.
            url2 (str): The URL path to the second shapefile.

        Returns:
            str: The GeoJSON representation of the spatial analysis result.
        """
        try:
            # Read shapefiles into GeoDataFrames
            gdf1 = gpd.read_file(url1)
            gdf2 = gpd.read_file(url2)

            # Perform spatial overlay to find intersections
            intersections = gpd.overlay(gdf1, gdf2, how='intersection')

            # Convert intersections to GeoJSON
            intersections_geojson = intersections.to_crs(epsg='4326').to_json()

            return intersections_geojson
        except Exception as e:
            print(f"Error performing spatial analysis: {e}")

    def add_tile_layer(self, tile_layer='OpenStreetMap'):
        """Adds a tile layer to the map.

        Args:
            tile_layer (str, optional): The name of the tile layer. Defaults to 'OpenStreetMap'.
        """
        folium.TileLayer(tile_layer).add_to(self.m)

    def add_layer_control(self):
        """Adds layer control to the map.

        Returns:
            LayerControl: The layer control object.
        """
        layer_control = folium.LayerControl().add_to(self.m)
        return layer_control

    def display(self):
        """Displays the map."""
        return self.m