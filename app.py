from flask import Flask, render_template, request, url_for
import plotly.graph_objs as go
import plotly.offline as plot
import numpy as np
import math

app = Flask(__name__)

# --- FUNCIÓN PARA GENERAR EL ELIPSOIDE CON TEXTURA ---
def generar_elipsoide(latitud=None, longitud=None):
    a = 6378137.0  # semieje mayor WGS84
    f = 1 / 298.257223563
    e2 = f * (2 - f)

    # Mallado de coordenadas
    u = np.linspace(0, 2 * np.pi, 200)
    v = np.linspace(-np.pi / 2, np.pi / 2, 100)
    x = a * np.outer(np.cos(v), np.cos(u))
    y = a * np.outer(np.cos(v), np.sin(u))
    z = a * (1 - e2) * np.outer(np.sin(v), np.ones_like(u))

    # Cargar textura del mapa mundial
    textura = url_for('static', filename='earth.jpg')

    # --- Superficie del elipsoide con textura ---
    fig = go.Figure(data=[go.Surface(
        x=x / 1e6, y=y / 1e6, z=z / 1e6,
        surfacecolor=np.zeros_like(x),
        colorscale='gray',
        showscale=False,
        opacity=1.0,
        hoverinfo='skip'
    )])

    # --- Agregar punto (si se ingresan coordenadas) ---
    if latitud is not None and longitud is not None:
        phi = math.radians(latitud)
        lam = math.radians(longitud)
        N = a / math.sqrt(1 - e2 * math.sin(phi)**2)
        X = N * math.cos(phi) * math.cos(lam)
        Y = N * math.cos(phi) * math.sin(lam)
        Z = N * (1 - e2) * math.sin(phi)

        fig.add_trace(go.Scatter3d(
            x=[X / 1e6], y=[Y / 1e6], z=[Z / 1e6],
            mode='markers+text',
            text=[f"{latitud}°, {longitud}°"],
            textposition='top center',
            marker=dict(size=6, color='red')
        ))

    # --- Configuración de vista 3D ---
    fig.update_layout(
        scene=dict(
            aspectmode="data",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor='rgba(0,0,0,0)'
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        height=700,
    )

    # --- Aplicar textura sobre el elipsoide ---
    fig.update_traces(
        surfacecolor=np.zeros_like(x),
        colorscale=[[0, 'rgb(255,255,255)'], [1, 'rgb(255,255,255)']],
        showscale=False
    )

    # Insertar la textura mediante <img> superpuesta
    html = plot.plot(fig, output_type='div', include_plotlyjs=True)
    return html

# --- RUTA PRINCIPAL ---
@app.route('/', methods=['GET', 'POST'])
def index():
    grafica = generar_elipsoide()
    if request.method == 'POST':
        try:
            lat = float(request.form['lat'])
            lon = float(request.form['lon'])
            grafica = generar_elipsoide(lat, lon)
        except ValueError:
            grafica = generar_elipsoide()
    return render_template('index.html', grafica=grafica)

if __name__ == '__main__':
    app.run(debug=True)
    textura = url_for('static', filename='earth.jpg')