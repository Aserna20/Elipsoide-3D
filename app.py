from flask import Flask, render_template, request
import plotly.graph_objects as go
import numpy as np
import math

app = Flask(__name__)

def gms_a_decimal(g, m, s):
    """Convierte grados, minutos, segundos a grados decimales."""
    signo = -1 if g < 0 else 1
    return signo * (abs(g) + m / 60 + s / 3600)

@app.route('/', methods=['GET', 'POST'])
def index():
    lat, lon = None, None

    if request.method == 'POST':
        # Intentar leer valores decimales
        lat_str = request.form.get('lat')
        lon_str = request.form.get('lon')

        # Leer grados, minutos y segundos
        try:
            lat_g = float(request.form.get('lat_g') or 0)
            lat_m = float(request.form.get('lat_m') or 0)
            lat_s = float(request.form.get('lat_s') or 0)
            lon_g = float(request.form.get('lon_g') or 0)
            lon_m = float(request.form.get('lon_m') or 0)
            lon_s = float(request.form.get('lon_s') or 0)
        except ValueError:
            lat_g = lat_m = lat_s = lon_g = lon_m = lon_s = 0

        if lat_str and lon_str:
            lat = float(lat_str)
            lon = float(lon_str)
        elif any([lat_g, lat_m, lat_s, lon_g, lon_m, lon_s]):
            lat = gms_a_decimal(lat_g, lat_m, lat_s)
            lon = gms_a_decimal(lon_g, lon_m, lon_s)

    # Parámetros del elipsoide (WGS84)
    a = 6378137
    b = 6356752.3142

    # Malla del elipsoide
    u = np.linspace(0, 2 * np.pi, 150)
    v = np.linspace(-np.pi / 2, np.pi / 2, 150)
    U, V = np.meshgrid(u, v)
    X = a * np.cos(V) * np.cos(U)
    Y = a * np.cos(V) * np.sin(U)
    Z = b * np.sin(V)

    # Crear figura 3D azul oceánica
    fig = go.Figure(data=[
        go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[[0, "#001f3f"], [0.5, "#0077b6"], [1, "#90e0ef"]],
            showscale=False,
            opacity=0.95
        )
    ])

    # Marcar punto
    if lat is not None and lon is not None:
        lat_r = math.radians(lat)
        lon_r = math.radians(lon)
        x_p = a * math.cos(lat_r) * math.cos(lon_r)
        y_p = a * math.cos(lat_r) * math.sin(lon_r)
        z_p = b * math.sin(lat_r)
        fig.add_trace(go.Scatter3d(
            x=[x_p], y=[y_p], z=[z_p],
            mode='markers+text',
            text=[f"{lat:.3f}°, {lon:.3f}°"],
            textposition="top center",
            marker=dict(size=6, color='red'),
            name='Punto'
        ))

    # Ajuste visual
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode='data',
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.1))
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0)
    )

    graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return render_template('index.html', graph_html=graph_html)

if __name__ == '__main__':
    app.run(debug=True)