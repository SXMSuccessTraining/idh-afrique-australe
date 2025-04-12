from flask import Flask, render_template_string, jsonify
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import io
import json

app = Flask(__name__)

@app.route("/")
def index():
    shapefile_path = "assets/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
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
    gdf_af["IDH"] = gdf_af["NAME"].map(lambda x: idh_data[x][0])
    gdf_af["Nom_FR"] = gdf_af["NAME"].map(lambda x: idh_data[x][1])

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('#f4f4f4')

    gdf_af.plot(ax=ax, color="white", edgecolor="black")
    bounds = gdf_af.total_bounds
    ax.set_xlim(bounds[0] - 5, bounds[2] + 5)
    ax.set_ylim(bounds[1] - 5, bounds[3] + 5)
    ax.axis('off')

    seychelles = Point(55.45, -4.6)
    ax.plot(seychelles.x, seychelles.y, 'o', color="white", markeredgecolor="black")

    buffer = io.StringIO()
    fig.savefig(buffer, format='svg', bbox_inches='tight')
    plt.close(fig)
    svg = buffer.getvalue()
    svg_content = '\n'.join(svg.split('\n')[4:])

    html_template = f"""
    <!DOCTYPE html>
    <html lang='fr'>
    <head>
        <meta charset='UTF-8'>
        <title>Jeu IDH SVG</title>
        <link rel='stylesheet' href='/static/style.css'>
    </head>
    <body>
        <h1>Associe chaque pays à sa catégorie d'IDH</h1>
        <div id="palette">
            <div class="pastille" data-cat="IDH très élevé (\u2265 0,800)" style="background-color:#00429d"></div>
            <div class="pastille" data-cat="IDH élevé (0,700 – 0,799)" style="background-color:#73a2c6"></div>
            <div class="pastille" data-cat="IDH moyen (0,550 – 0,699)" style="background-color:#fdb863"></div>
            <div class="pastille" data-cat="IDH faible (< 0,550)" style="background-color:#93003a"></div>
        </div>
        <div id="map">{svg_content}</div>
        <div id="feedback"></div>
        <script src="/static/script.js"></script>
    </body>
    </html>
    """
    return render_template_string(html_template)

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
    app.run(debug=True)
