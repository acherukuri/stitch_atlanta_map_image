import os
from flask import Flask, send_file, request
from generate_atlanta_map import StitchedAtlantaMapGenerator

app = Flask(__name__)

@app.route('/', methods=['GET'])
def download_atlanta_map_image():
    try:
        map_manifest_url = request.args.get('map_manifest_url')
        if map_manifest_url is None:
            return "Error: 'map_manifest_url' parameter is required", 400

        image_file_name = StitchedAtlantaMapGenerator(map_manifest_url).generate()
        return send_file(f"./{image_file_name}", as_attachment=True, download_name='atlanta_map.jpg')
    except Exception as e:
        println(e)
        return "An error occurred while downloading the image. Please try again later.", 500
    finally:
        os.remove(image_file_name)

if __name__ == '__main__':
    app.run(debug=True)