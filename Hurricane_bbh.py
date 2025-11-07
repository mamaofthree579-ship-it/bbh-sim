import numpy as np
import plotly.graph_objects as go

# Build initial grid
theta = np.linspace(0, np.pi, 50)
phi = np.linspace(0, 2*np.pi, 50)
x = np.outer(np.sin(theta), np.cos(phi))
y = np.outer(np.sin(theta), np.sin(phi))
z = np.outer(np.cos(theta), np.ones_like(phi))

# Core frame 0
surface = go.Surface(x=x, y=y, z=z, colorscale="Inferno", showscale=False)

# Animation frames – rotate around z axis
frames = []
for angle in np.linspace(0, 2*np.pi, 40):
    rot_x = np.cos(angle)*x - np.sin(angle)*y
    rot_y = np.sin(angle)*x + np.cos(angle)*y
    frames.append(go.Frame(data=[go.Surface(x=rot_x, y=rot_y, z=z,
                                            colorscale="Inferno", showscale=False)]))

fig = go.Figure(
    data=[surface],
    frames=frames,
    layout=go.Layout(
        scene=dict(aspectmode="data"),
        updatemenus=[dict(type="buttons", showactive=False,
            buttons=[dict(label="Play", method="animate", args=[None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}]),
                     dict(label="Pause", method="animate", args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}])])]
    )
)
