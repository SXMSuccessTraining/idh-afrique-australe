from flask import Flask, render_template_string, jsonify
import geopandas as gpd
import svgwrite
from shapely.geometry import Point, MultiPolygon
import io
import json
import re
import os

app = Flask(__name__)

@app.route("/")
def index():
    basedir = os.path.abspath(os.path.dirname(__file__))
    shapefile_path = os.path.join(basedir, "assets", "ne_10m_admin_0_countries.shp")
    gdf = gpd.read_file(shapefile_path)

    idh_data = {
        "South Africa": (0.717, "Afrique du Sud"),
        "Angola": (0.591, "Angola"),
        "Botswana": (0.708, "Botswana"),
        "Eswatini": (0.610, "Eswatini"),
        "Lesotho": (0.521, "Lesotho"),
        "Namibia": (0.610, "Namibie"),
        "Zambia": (0.609, "Zambie"),
        "Zimbabwe": (0.550, "Zimbabwe"),
        "Mozambique": (0.461, "Mozambique"),
        "Malawi": (0.508, "Malawi"),
        "Seychelles": (0.802, "Seychelles")
    }

    gdf_af = gdf[gdf['NAME'].isin(idh_data.keys())].copy()
    gdf_af["Nom_FR"] = gdf_af["NAME"].map(lambda x: idh_data[x][1])

    def sanitize_id(name):
        return re.sub(r"[^a-zA-Z0-9_-]", "_", name)

    minx, miny, maxx, maxy = gdf_af.total_bounds
    width, height = 600, 700
    scale_x = width / (maxx - minx)
    scale_y = height / (maxy - miny)

    scale_ratio = 0.65
    width *= scale_ratio
    height *= scale_ratio
    scale_x *= scale_ratio
    scale_y *= scale_ratio

    dwg = svgwrite.Drawing(size=(f"{width}px", f"{height}px"))
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill='#f4f4f4'))

    for _, row in gdf_af.iterrows():
        shape = row.geometry
        name = row['NAME']
        if name == "Angola":
            country_id = "Angola"
        else:
            country_id = sanitize_id(name)
        label = row['Nom_FR']
        if shape.geom_type == 'MultiPolygon':
            for polygon in shape.geoms:
                path = svg_path_from_poly(polygon, minx, miny, scale_x, scale_y, height)
                dwg.add(dwg.path(d=path, fill='white', stroke='black', id=country_id))
        elif shape.geom_type == 'Polygon':
            path = svg_path_from_poly(shape, minx, miny, scale_x, scale_y, height)
            dwg.add(dwg.path(d=path, fill='white', stroke='black', id=country_id))
        centroid = shape.centroid
        cx = (centroid.x - minx) * scale_x
        cy = height - (centroid.y - miny) * scale_y
        dwg.add(dwg.text(label, insert=(cx, cy), font_size="8px", text_anchor="middle", fill="black"))

    seychelles = Point(55.45, -4.6)
    x = (seychelles.x - minx) * scale_x
    y = height - (seychelles.y - miny) * scale_y
    dwg.add(dwg.circle(center=(x, y), r=5, fill='white', stroke='black', id='Seychelles'))

    svg_content = dwg.tostring()

    html_template = f"""
    <!DOCTYPE html>
    <html lang='fr'>
    <head>
        <meta charset='UTF-8'>
        <title>Jeu IDH SVG</title>
        <link rel='stylesheet' href='/static/style.css'>
        <style>
            #layout {{ display: flex; justify-content: center; align-items: flex-start; gap: 40px; }}
            #palette {{ display: flex; flex-direction: column; gap: 20px; margin-left: 20px; }}
            .pastille {{ width: 60px; height: 60px; border-radius: 50%; border: 2px solid black; cursor: pointer; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; text-align: center; padding: 2px; }}
            #map {{ display: flex; justify-content: center; }}
            #feedback {{ width: 220px; min-height: 60px; text-align: center; font-weight: bold; margin-top: 30px; }}
            h1 {{ text-align: center; }}
            #subtitle {{ text-align: center; font-style: italic; margin-bottom: 20px; }}
            footer {{ text-align: center; font-size: 0.9em; margin-top: 30px; color: #444; }}
        </style>
    </head>
    <body>
        <h1>Associe chaque pays à sa catégorie d'IDH</h1>
        <div id="subtitle">Cette activité vous permet d'observer les contrastes de développement importants qui caractérisent l'Afrique australe.</div>
        <div id="layout">
            <div id="palette">
                <div class="pastille" data-cat="IDH très élevé (≥ 0,800)" style="background-color:#00429d">IDH très élevé<br>≥ 0,800</div>
                <div class="pastille" data-cat="IDH élevé (0,700 – 0,799)" style="background-color:#73a2c6">IDH élevé<br>0,700 – 0,799</div>
                <div class="pastille" data-cat="IDH moyen (0,550 – 0,699)" style="background-color:#fdb863">IDH moyen<br>0,550 – 0,699</div>
                <div class="pastille" data-cat="IDH faible (< 0,550)" style="background-color:#93003a">IDH faible<br>&lt; 0,550</div>
            </div>
            <div id="map">{svg_content}</div>
            <div id="feedback"></div>
        </div>
        <footer>Lycée Robert Weinum (Saint-Martin). Idée originale : Claire Guthmann ; Développement : Sullivan Munoz</footer>
        <script src="/static/script.js"></script>
    </body>
    </html>
    """
    return render_template_string(html_template)

def svg_path_from_poly(polygon, minx, miny, scale_x, scale_y, height):
    exterior_coords = [
        ((x - minx) * scale_x, height - (y - miny) * scale_y)
        for x, y in polygon.exterior.coords
    ]
    path = f"M {exterior_coords[0][0]},{exterior_coords[0][1]} "
    path += " ".join([f"L {x},{y}" for x, y in exterior_coords[1:]]) + " Z"
    return path

@app.route("/data/idh")
def get_idh():
    idh_data = {
        "South Africa": {"nom_fr": "Afrique du Sud", "idh": 0.717, "categorie": "IDH élevé (0,700 – 0,799)"},
        "Angola": {"nom_fr": "Angola", "idh": 0.591, "categorie": "IDH moyen (0,550 – 0,699)"},
        "Botswana": {"nom_fr": "Botswana", "idh": 0.708, "categorie": "IDH élevé (0,700 – 0,799)"},
        "Eswatini": {"nom_fr": "Eswatini", "idh": 0.610, "categorie": "IDH moyen (0,550 – 0,699)"},
        "Lesotho": {"nom_fr": "Lesotho", "idh": 0.521, "categorie": "IDH faible (< 0,550)"},
        "Namibia": {"nom_fr": "Namibie", "idh": 0.610, "categorie": "IDH moyen (0,550 – 0,699)"},
        "Zambia": {"nom_fr": "Zambie", "idh": 0.609, "categorie": "IDH moyen (0,550 – 0,699)"},
        "Zimbabwe": {"nom_fr": "Zimbabwe", "idh": 0.550, "categorie": "IDH moyen (0,550 – 0,699)"},
        "Mozambique": {"nom_fr": "Mozambique", "idh": 0.461, "categorie": "IDH faible (< 0,550)"},
        "Malawi": {"nom_fr": "Malawi", "idh": 0.508, "categorie": "IDH faible (< 0,550)"},
        "Seychelles": {"nom_fr": "Seychelles", "idh": 0.802, "categorie": "IDH très élevé (≥ 0,800)"}
    }
    return jsonify(idh_data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
