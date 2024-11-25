import streamlit as st
import json
import streamlit as st
import json
import base64
import numpy as np
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Import local modules
from ley_line_generator import (
    generate_nodes_and_ley_lines,
    validate_platonic_solid_nodes,
    validate_ley_line_connections,
    suggest_distance_parameters
)
from utils import create_globe_visualization, get_preset_configurations, save_presets

# Set up page config
st.set_page_config(layout="wide", page_title="Ley Line Network Generator")

# Load custom CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
    <div class='main-header'>
        <h1>Ley Line Network Generator</h1>
        <p>Generate and visualize ley line networks for your game world</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar for controls
with st.sidebar:
    st.header("Configuration")
    
    # Preset selector
    st.subheader("Presets")
    presets = get_preset_configurations()
    selected_preset = st.selectbox(
        "Select a preset",
        ["Custom"] + list(presets.keys()),
        key="preset_selector"
    )
    
    # Configuration section
    if selected_preset != "Custom":
        preset_config = presets[selected_preset]
        solid_type = preset_config["solid_type"]
        radius = preset_config["radius"]
        max_distance = preset_config["max_distance"]
        
        # Show current preset values
        st.subheader("Current Preset Configuration")
        st.write(f"Solid Type: {solid_type}")
        st.write(f"Radius: {radius} km")
        st.write(f"Max Distance: {max_distance} km")
        
        # Delete preset button
        if st.button("Delete Selected Preset", key="delete_preset"):
            del presets[selected_preset]
            save_presets(presets)
            st.success(f"Preset '{selected_preset}' deleted successfully!")
            st.rerun()
    else:
        # Manual configuration
        st.subheader("Manual Configuration")
        
        solid_type = st.selectbox(
            "Platonic Solid Type",
            ["tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"],
            help="The base platonic solid used to generate the network",
            key="solid_type_selector"
        )
        
        radius = st.number_input(
            "Sphere Radius (km)",
            min_value=1.0,
            max_value=10000.0,
            value=6371.0,
            help="Radius of the sphere in kilometers",
            key="radius_input"
        )
        
        max_distance = st.number_input(
            "Maximum Ley Line Distance (km)",
            min_value=1.0,
            max_value=10000.0,
            value=5000.0,
            help="Maximum distance between nodes to create a ley line",
            key="max_distance_input"
        )
    
    # Save current configuration as preset
    save_preset = st.button("Save Current as Preset", key="save_preset")
    if save_preset:
        preset_name = st.text_input("Enter preset name", key="preset_name")
        if preset_name and preset_name != "Custom":
            new_preset = {
                "solid_type": solid_type,
                "radius": radius,
                "max_distance": max_distance
            }
            presets[preset_name] = new_preset
            save_presets(presets)
            st.success(f"Preset '{preset_name}' saved successfully!")
            st.rerun()

# Main content area
try:
    # Generate the network
    data = generate_nodes_and_ley_lines(
        solid_type=solid_type,
        radius=radius,
        max_distance=max_distance
    )
    
    # Geo-location inputs in sidebar
    st.sidebar.subheader("Reference Point")
    ref_lat = st.sidebar.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0,
                                    help="Enter latitude in degrees (-90 to 90)",
                                    key="reference_latitude")
    ref_lon = st.sidebar.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0,
                                    help="Enter longitude in degrees (-180 to 180)",
                                    key="reference_longitude")
    reference_point = {"latitude": ref_lat, "longitude": ref_lon} if ref_lat != 0 or ref_lon != 0 else None
    
    # Create visualization
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Network Visualization")
        fig = create_globe_visualization(data["nodes"], data["ley_lines"], radius, reference_point)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Network Statistics")
        st.write(f"Total Nodes: {len(data['nodes'])}")
        st.write(f"Total Ley Lines: {len(data['ley_lines'])}")
        
        primary_lines = sum(1 for line in data['ley_lines'] if line['category'] == 'primary')
        st.write(f"Primary Ley Lines: {primary_lines}")
        st.write(f"Secondary Ley Lines: {len(data['ley_lines']) - primary_lines}")
    
    # Batch Generation section
    st.header("Batch Generation")
    tab1, tab2 = st.tabs(["Configuration", "Results"])
    
    with tab1:
        st.write("Generate multiple network configurations at once")
        
        # Simplified batch configuration options
        batch_solid_types = st.multiselect(
            "Select Platonic Solids",
            ["tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"],
            default=["tetrahedron"],
            help="Choose one or more platonic solids for batch generation"
        )
        
        batch_radius = st.number_input(
            "Sphere Radius (km)",
            min_value=1.0,
            value=6371.0,
            help="Radius of the sphere in kilometers (Earth's radius ≈ 6371 km)",
            key="batch_radius_input"
        )
        
        batch_max_distance = st.number_input(
            "Maximum Ley Line Distance (km)",
            min_value=1.0,
            max_value=batch_radius * np.pi,  # Maximum possible distance on sphere
            value=5000.0,
            help="Maximum distance between nodes to create a ley line",
            key="batch_max_distance_input"
        )
        
        # Add auto-adjust option
        auto_adjust = st.checkbox("Auto-adjust parameters when no connections are made", value=True)
            
        # Generate batch button
        if st.button("Generate Batch"):
            batch_results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_configs = len(batch_solid_types)
            current_config = 0
            
            for solid in batch_solid_types:
                status_text.text(f"Generating: {solid}")
                try:
                    # Generate initial configuration
                    config_data = generate_nodes_and_ley_lines(
                        solid_type=solid,
                        radius=batch_radius,
                        max_distance=batch_max_distance,
                        auto_adjust=auto_adjust
                    )
                    
                    # Validate the configuration
                    nodes_valid, nodes_message = validate_platonic_solid_nodes(
                        config_data["nodes"],
                        solid
                    )
                    connections_valid, connections_message = validate_ley_line_connections(
                        config_data["nodes"],
                        config_data["ley_lines"],
                        batch_max_distance
                    )
                    
                    # Get parameter suggestions
                    parameter_suggestions = suggest_distance_parameters(config_data["nodes"])
                    
                    batch_results.append({
                        "configuration": {
                            "solid_type": solid,
                            "radius": batch_radius,
                            "max_distance": batch_max_distance,
                            "auto_adjust_enabled": auto_adjust
                        },
                        "data": config_data,
                        "validation": {
                            "nodes_valid": nodes_valid,
                            "nodes_message": nodes_message,
                            "connections_valid": connections_valid,
                            "connections_message": connections_message,
                            "parameter_suggestions": parameter_suggestions
                        },
                        "statistics": {
                            "total_nodes": len(config_data["nodes"]),
                            "total_ley_lines": len(config_data["ley_lines"]),
                            "primary_ley_lines": sum(1 for line in config_data["ley_lines"] if line["category"] == "primary")
                        }
                    })
                    
                    # Display validation results and connection statistics in a cleaner format
                    with st.container():
                        st.markdown(f"### Configuration Results - {solid}")
                        
                        # Create two columns for original and adjusted parameters
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Original Parameters**")
                            st.write(f"Max Distance: {batch_max_distance:.2f} km")
                            st.write(f"Auto-adjust: {'Enabled' if auto_adjust else 'Disabled'}")
                        
                        with col2:
                            st.markdown("**Suggested Parameters**")
                            st.write(f"Min Distance: {parameter_suggestions['min_distance']:.2f} km")
                            st.write(f"Max Distance: {parameter_suggestions['max_distance']:.2f} km")
                        
                        # Display validation results
                        st.markdown("**Validation Results**")
                        col3, col4 = st.columns(2)
                        
                        with col3:
                            st.metric(
                                "Node Validation",
                                "Passed" if nodes_valid else "Failed",
                                nodes_message
                            )
                        
                        with col4:
                            st.metric(
                                "Connection Validation",
                                "Passed" if connections_valid else "Failed",
                                connections_message
                            )
                        
                        # Display connection statistics
                        st.markdown("**Connection Statistics**")
                        stats = config_data.get("metadata", {}).get("connection_stats", {})
                        col5, col6 = st.columns(2)
                        
                        with col5:
                            attempted = stats.get("attempted", 0)
                            successful = stats.get("successful", 0)
                            success_rate = (successful / attempted * 100) if attempted > 0 else 0
                            st.metric(
                                "Connection Success Rate",
                                f"{success_rate:.1f}%",
                                f"{successful}/{attempted} connections"
                            )
                        
                        with col6:
                            st.metric(
                                "Network Density",
                                f"{len(config_data['ley_lines'])}/{len(config_data['nodes'])} nodes",
                                f"Average: {len(config_data['ley_lines'])/len(config_data['nodes']):.1f} lines per node"
                            )
                    current_config += 1
                    progress_bar.progress(current_config / total_configs)
                    
                except ValueError as e:
                    st.warning(f"Skipping invalid configuration - {solid}: {str(e)}")
                    current_config += 1
                    progress_bar.progress(current_config / total_configs)
            
            # Export batch results
            json_str = json.dumps(batch_results, indent=2)
            b64 = base64.b64encode(json_str.encode()).decode()
            href = f'<a href="data:file/json;base64,{b64}" download="batch_configurations.json">Download Batch Results (JSON)</a>'
            st.markdown(href, unsafe_allow_html=True)
            
            # Generate timestamp for exports
            timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M")
            
            # Display final summary in Results tab
            tab2.markdown("---")
            tab2.subheader("Batch Generation Summary")
            tab2.write(f"Total configurations generated: {len(batch_results)}")
            
            # Create a more detailed summary table
            summary_data = []
            for result in batch_results:
                config = result['configuration']
                stats = result['statistics']
                validation = result.get('validation', {})
                
                success_rate = (stats['total_ley_lines'] / stats['total_nodes'] * 100) if stats['total_nodes'] > 0 else 0
                
                summary_data.append({
                    'Configuration': config['solid_type'].capitalize(),
                    'Nodes': stats['total_nodes'],
                    'Ley Lines': stats['total_ley_lines'],
                    'Primary Lines': stats['primary_ley_lines'],
                    'Success Rate': f"{success_rate:.1f}%",
                    'Validation': "✅ Passed" if validation.get('nodes_valid', False) and validation.get('connections_valid', False) else "⚠️ Issues Found"
                })
            
            summary_df = pd.DataFrame(summary_data)
            
            tab2.dataframe(summary_df, hide_index=True)
            
            # Display results in a table
            summary_data = []
            for result in batch_results:
                config = result["configuration"]
                stats = result["statistics"]
                summary_data.append({
                    "Solid Type": config["solid_type"],
                    "Radius (km)": config["radius"],
                    "Max Distance (km)": config["max_distance"],
                    "Nodes": stats["total_nodes"],
                    "Ley Lines": stats["total_ley_lines"],
                    "Primary Lines": stats["primary_ley_lines"]
                })
            
            st.dataframe(pd.DataFrame(summary_data))

    # Export section
    st.subheader("Export Current Configuration")
    col3, col4 = st.columns(2)
    
    with col3:
        # Export as JSON
        json_str = json.dumps(data, indent=2)
        b64 = base64.b64encode(json_str.encode()).decode()
        href = f'<a href="data:file/json;base64,{b64}" download="ley_line_network.json">Download Current Configuration (JSON)</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    with col4:
        # Preview JSON
        if st.button("Preview Current Configuration"):
            st.json(data)

except Exception as e:
    st.error(f"Error generating network: {str(e)}")
    st.write("Please adjust your parameters and try again.")
