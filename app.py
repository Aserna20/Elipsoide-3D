from flask import Flask, render_template, request
import plotly.graph_objects as go
import numpy as np
import math

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    lat, lon = None, None
    if request.method == 'POST':
        lat = float(request.form['lat'])
        lon = float(request.form['lon'])

    # Parámetros del elipsoide WGS84
    a = 6378137
    b = 6356752.3142

    # Mallado del elipsoide
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(-np.pi/2, np.pi/2, 100)
    U, V = np.meshgrid(u, v)

    X = a * np.cos(V) * np.cos(U)
    Y = a * np.cos(V) * np.sin(U)
    Z = b * np.sin(V)

    # Figura 3D con textura
    fig = go.Figure(
        data=[
            go.Surface(
                x=X, y=Y, z=Z,
                surfacecolor=np.zeros_like(Z),
                colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']],
                showscale=False,
                opacity=1.0,
                name="Elipsoide"
            )
        ]
    )

    # Si se ingresan coordenadas, marcar punto
    if lat is not None and lon is not None:
        lat_r = math.radians(lat)
        lon_r = math.radians(lon)
        x_p = a * math.cos(lat_r) * math.cos(lon_r)
        y_p = a * math.cos(lat_r) * math.sin(lon_r)
        z_p = b * math.sin(lat_r)

        fig.add_trace(go.Scatter3d(
            x=[x_p], y=[y_p], z=[z_p],
            mode='markers',
            marker=dict(size=6, color='red'),
            name='Punto marcado'
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(showbackground=False, visible=False),
            yaxis=dict(showbackground=False, visible=False),
            zaxis=dict(showbackground=False, visible=False),
            aspectmode='data',
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.0))
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0)
    )

    graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template('index.html', graph_html=graph_html)

if __name__ == '__main__':
    app.run(debug=True)