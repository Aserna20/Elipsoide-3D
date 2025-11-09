from flask import Flask, render_template, request
import plotly.graph_objs as go
import plotly.offline as plot
import numpy as np
import math

app = Flask(__name__)

# --- Función para generar el elipsoide WGS84 ---
def generar_elipsoide(latitud=None, longitud=None):
    a = 6378137.0
    f = 1 / 298.257223563
    e2 = f * (2 - f)

    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(-np.pi / 2, np.pi / 2, 100)
    x = a * np.outer(np.cos(v), np.cos(u))
    y = a * np.outer(np.cos(v), np.sin(u))
    z = a * np.outer((1 - e2), np.sin(v))

    fig = go.Figure()

    fig.add_trace(go.Surface(
        x=x, y=y, z=z,
        colorscale="Earth",
        showscale=False,
        opacity=0.9
    ))

    # Si el usuario ingresó una coordenada, la calculamos y graficamos
    if latitud is not None and longitud is not None:
        phi = math.radians(latitud)
        lam = math.radians(longitud)
        N = a / math.sqrt(1 - e2 * math.sin(phi) ** 2)
        X = N * math.cos(phi) * math.cos(lam)
        Y = N * math.cos(phi) * math.sin(lam)
        Z = N * (1 - e2) * math.sin(phi)

        fig.add_trace(go.Scatter3d(
            x=[X], y=[Y], z=[Z],
            mode='markers+text',
            text=[f"Lat: {latitud}°, Lon: {longitud}°"],
            textposition='top center',
            marker=dict(size=6, color='red')
        ))

    fig.update_layout(
        scene=dict(
            aspectmode="data",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False)
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return plot.plot(fig, output_type='div')

@app.route('/', methods=['GET', 'POST'])
def index():
    grafica = generar_elipsoide()
    if request.method == 'POST':
        try:
            lat = float(request.form['lat'])
            lon = float(request.form['lon'])
            grafica = generar_elipsoide(lat, lon)
        except ValueError:
            pass

    return render_template('index.html', grafica=grafica)

if __name__ == '__main__':
    app.run(debug=True)
