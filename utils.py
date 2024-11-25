import plotly.graph_objects as go
import json
import numpy as np

def create_globe_visualization(nodes, ley_lines, radius, reference_point=None):
    """
    Create a 3D globe visualization using Plotly.
    
    Args:
        nodes: List of node dictionaries
        ley_lines: List of ley line dictionaries
        radius: Sphere radius in kilometers
        reference_point: Optional dictionary with latitude and longitude for reference point
    """
    fig = go.Figure()

    # Add the sphere surface
    phi = np.linspace(0, 2*np.pi, 100)
    theta = np.linspace(-np.pi/2, np.pi/2, 100)
    phi, theta = np.meshgrid(phi, theta)
    
    x = radius * np.cos(theta) * np.cos(phi)
    y = radius * np.cos(theta) * np.sin(phi)
    z = radius * np.sin(theta)
    
    fig.add_surface(x=x, y=y, z=z, opacity=0.3, 
                   colorscale='Blues', showscale=False)
    
    # Add reference lines if a point is provided
    if reference_point:
        lat = np.radians(reference_point['latitude'])
        lon = np.radians(reference_point['longitude'])
        
        # Add equator
        eq_phi = np.linspace(0, 2*np.pi, 100)
        eq_x = radius * np.cos(eq_phi)
        eq_y = radius * np.sin(eq_phi)
        eq_z = np.zeros_like(eq_phi)
        fig.add_scatter3d(x=eq_x, y=eq_y, z=eq_z, mode='lines',
                         line=dict(color='gray', width=1),
                         name='Equator')
        
        # Add meridian through the point
        mer_theta = np.linspace(-np.pi/2, np.pi/2, 100)
        mer_x = radius * np.cos(mer_theta) * np.cos(lon)
        mer_y = radius * np.cos(mer_theta) * np.sin(lon)
        mer_z = radius * np.sin(mer_theta)
        fig.add_scatter3d(x=mer_x, y=mer_y, z=mer_z, mode='lines',
                         line=dict(color='gray', width=1),
                         name='Meridian')
        
        # Add reference point
        x_ref = radius * np.cos(lat) * np.cos(lon)
        y_ref = radius * np.cos(lat) * np.sin(lon)
        z_ref = radius * np.sin(lat)
        fig.add_scatter3d(x=[x_ref], y=[y_ref], z=[z_ref],
                         mode='markers',
                         marker=dict(size=8, color='yellow'),
                         name='Reference Point')

    # Add nodes
    node_x = []
    node_y = []
    node_z = []
    node_text = []
    
    for node in nodes:
        lat = np.radians(node['coordinates']['latitude'])
        lon = np.radians(node['coordinates']['longitude'])
        
        x_pos = radius * np.cos(lat) * np.cos(lon)
        y_pos = radius * np.cos(lat) * np.sin(lon)
        z_pos = radius * np.sin(lat)
        
        node_x.append(x_pos)
        node_y.append(y_pos)
        node_z.append(z_pos)
        node_text.append(f"Node: {node['id']}<br>Lat: {node['coordinates']['latitude']:.2f}°<br>Lon: {node['coordinates']['longitude']:.2f}°")

    fig.add_scatter3d(x=node_x, y=node_y, z=node_z,
                     mode='markers',
                     marker=dict(size=8, color='red'),
                     text=node_text,
                     hoverinfo='text',
                     name='Nodes')

    # Add ley lines
    for line in ley_lines:
        node1_id = line['nodes'][0]
        node2_id = line['nodes'][1]
        
        node1 = next(node for node in nodes if node['id'] == node1_id)
        node2 = next(node for node in nodes if node['id'] == node2_id)
        
        lat1 = np.radians(node1['coordinates']['latitude'])
        lon1 = np.radians(node1['coordinates']['longitude'])
        lat2 = np.radians(node2['coordinates']['latitude'])
        lon2 = np.radians(node2['coordinates']['longitude'])
        
        x = [radius * np.cos(lat1) * np.cos(lon1),
             radius * np.cos(lat2) * np.cos(lon2)]
        y = [radius * np.cos(lat1) * np.sin(lon1),
             radius * np.cos(lat2) * np.sin(lon2)]
        z = [radius * np.sin(lat1),
             radius * np.sin(lat2)]
        
        line_color = 'yellow' if line['category'] == 'primary' else 'cyan'
        
        fig.add_scatter3d(x=x, y=y, z=z,
                         mode='lines',
                         line=dict(color=line_color, width=2),
                         hoverinfo='none',
                         showlegend=False)

    fig.update_layout(
        scene=dict(
            aspectmode='data',
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=1.5)
            ),
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z'
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    return fig

def load_presets():
    """Load preset configurations from the presets file."""
    try:
        with open("presets.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default presets if file doesn't exist
        default_presets = {
            "Earth-scale Network": {
                "solid_type": "icosahedron",
                "radius": 6371,
                "max_distance": 5000
            },
            "Compact Network": {
                "solid_type": "octahedron",
                "radius": 1000,
                "max_distance": 800
            },
            "Dense Network": {
                "solid_type": "dodecahedron",
                "radius": 2000,
                "max_distance": 2000
            }
        }
        save_presets(default_presets)
        return default_presets

def save_presets(presets):
    """Save preset configurations to the presets file."""
    with open("presets.json", "w") as f:
        json.dump(presets, f, indent=4)

def get_preset_configurations():
    """Return preset configurations for quick setup."""
    return load_presets()
