import time
import shutil
import os
import requests
from PIL import Image
from io import BytesIO

class StitchedAtlantaMapGenerator:
    def __init__(self, map_manifest_url):
        self.map_manifest_url = map_manifest_url

    def __compute_map_manifest_info_url(self):
        # TODO validate the manifest url
        self.__image_resource_name = self.map_manifest_url.split("/")[-2]
        map_manifest_info_url = f"http://www.digitalgallery.emory.edu/luna/servlet/iiif/{self.__image_resource_name}/info.json"
        self.__map_manifest_info_url = map_manifest_info_url

    def __download_all_tiles(self):
        # Create output directory
        self.__timestamp_suffix_for_images = time.monotonic_ns()
        self.__tiles_directory_name = f"tiles-{self.__timestamp_suffix_for_images}"
        os.makedirs(self.__tiles_directory_name)
        # Fetch and parse JSON
        info = requests.get(self.__map_manifest_info_url).json()
        tile_width = info['tiles'][0]['width']
        tile_height = info['tiles'][0]['height']
        self.__image_width = info['width']
        self.__image_height = info['height']

        # Download tiles
        self.__image_tiles = []
        for y in range(0, self.__image_height, tile_height):
            for x in range(0, self.__image_width, tile_width):
                width = min(tile_width, self.__image_width - x)
                height = min(tile_height, self.__image_height - y)
                region = f"{x},{y},{width},{height}"
                tile_url = f"http://www.digitalgallery.emory.edu/luna/servlet/iiif/{self.__image_resource_name}/{region}/full/0/default.jpg"
                
                print(f"Downloading {tile_url}")
                response = requests.get(tile_url)
                tile_path = f"{self.__tiles_directory_name}/tile_{x}_{y}.jpg"
                with open(tile_path, "wb") as tile_file:
                    tile_file.write(response.content)
                self.__image_tiles.append((x, y, Image.open(tile_path)))

    def __stitch_image_tiles(self):
        try:
            self.__final_image_name = f"stitched_image-{self.__timestamp_suffix_for_images}.jpg"
            # Stitch tiles
            final_image = Image.new("RGB", (self.__image_width, self.__image_height))
            for x, y, tile in self.__image_tiles:
                final_image.paste(tile, (x, y))


            # Save the final image
            final_image.save(self.__final_image_name)
            print(f"Image stitching complete! Saved as {self.__final_image_name}")
        finally:
            shutil.rmtree(self.__tiles_directory_name)

    def generate(self):
        self.__compute_map_manifest_info_url()
        self.__download_all_tiles()
        self.__stitch_image_tiles()
        
        return self.__final_image_name
