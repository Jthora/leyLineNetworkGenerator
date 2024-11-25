import math
import json
import logging
import numpy as np
import os

import statistics

def validate_platonic_solid_nodes(nodes: list, solid_type: str) -> tuple:
    """
    Verify node positions match expected geometry for the given platonic solid.
    
    Args:
        nodes (list): List of node dictionaries.
        solid_type (str): Type of Platonic solid.
        
    Returns:
        tuple: (bool, str) - (is_valid, message)
    """
    expected_counts = {
        'tetrahedron': 4,
        'cube': 8,
        'octahedron': 6,
        'dodecahedron': 12,
        'icosahedron': 12
    }
    
    if len(nodes) != expected_counts[solid_type]:
        return False, f"Invalid number of nodes. Expected {expected_counts[solid_type]}, got {len(nodes)}."
    
    # Verify node coordinates are within valid ranges
    for node in nodes:
        lat = node['coordinates']['latitude']
        lon = node['coordinates']['longitude']
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return False, f"Invalid coordinates for node {node['id']}: lat={lat}, lon={lon}"
            
    return True, "Node positions are valid."

def validate_ley_line_connections(nodes: list, ley_lines: list, max_distance: float) -> tuple:
    """
    Verify all connections are within the specified maximum distance.
    
    Args:
        nodes (list): List of node dictionaries.
        ley_lines (list): List of ley line dictionaries.
        max_distance (float): Maximum allowed distance between connected nodes.
        
    Returns:
        tuple: (bool, str) - (is_valid, message)
    """
    node_dict = {node['id']: node for node in nodes}
    invalid_connections = []
    
    for line in ley_lines:
        node1 = node_dict[line['nodes'][0]]
        node2 = node_dict[line['nodes'][1]]
        
        lat1 = math.radians(node1['coordinates']['latitude'])
        lon1 = math.radians(node1['coordinates']['longitude'])
        lat2 = math.radians(node2['coordinates']['latitude'])
        lon2 = math.radians(node2['coordinates']['longitude'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = 6371 * c  # Using Earth's radius
        
        if distance > max_distance:
            invalid_connections.append((line['id'], distance))
    
    if invalid_connections:
        details = '\n'.join([f"Line {line_id}: {dist:.2f} km" for line_id, dist in invalid_connections])
        return False, f"Found {len(invalid_connections)} connections exceeding maximum distance:\n{details}"
        
    return True, f"All {len(ley_lines)} connections are within maximum distance."

def suggest_distance_parameters(nodes: list) -> dict:
    """
    Calculate and suggest optimal distance parameters based on node distribution.
    
    Args:
        nodes (list): List of node dictionaries.
        
    Returns:
        dict: Suggested parameters including min_distance and max_distance
    """
    all_distances = []
    for i, node1 in enumerate(nodes):
        lat1 = math.radians(node1['coordinates']['latitude'])
        lon1 = math.radians(node1['coordinates']['longitude'])
        
        for node2 in nodes[i+1:]:
            lat2 = math.radians(node2['coordinates']['latitude'])
            lon2 = math.radians(node2['coordinates']['longitude'])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = 6371 * c
            all_distances.append(distance)
    
    if not all_distances:
        return {
            'min_distance': 0,
            'max_distance': 6371 * math.pi,  # Half circumference
            'message': "No node pairs found for distance calculation"
        }
    
    min_dist = min(all_distances)
    median_dist = statistics.median(all_distances)
    
    suggested_max = median_dist * 1.5
    suggested_min = min_dist * 0.8
    
    return {
        'min_distance': suggested_min,
        'max_distance': suggested_max,
        'median_distance': median_dist,
        'message': f"Suggested parameters based on node distribution:\n"
                  f"Minimum distance: {suggested_min:.2f} km\n"
                  f"Maximum distance: {suggested_max:.2f} km\n"
                  f"Median distance: {median_dist:.2f} km"
    }
# Configure logging with a default level and allow external configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_platonic_solid(solid_type: str = 'icosahedron', radius: float = 6371) -> list:
    """
    Generate nodes based on Platonic solids mapped onto a sphere.

    Args:
        solid_type (str): Type of Platonic solid. Options are 'tetrahedron', 'cube',
                          'octahedron', 'dodecahedron', 'icosahedron'.
        radius (float): Radius of the sphere in kilometers.

    Returns:
        list: List of node dictionaries with coordinates and metadata.

    Raises:
        ValueError: If an unsupported solid_type is provided or radius is non-positive.
    """
    logging.info(f"Generating nodes for a {solid_type} mapped onto a sphere with radius {radius} km.")

    # Validate inputs
    if radius <= 0:
        raise ValueError("Radius must be a positive number.")

    # Define the vertices for each Platonic solid
    if solid_type == 'tetrahedron':
        # Tetrahedron vertices
        points = np.array([
            [1, 1, 1],
            [-1, -1, 1],
            [-1, 1, -1],
            [1, -1, -1]
        ])
    elif solid_type == 'cube':
        # Cube vertices
        points = np.array([
            [1, 1, 1],
            [1, 1, -1],
            [1, -1, 1],
            [1, -1, -1],
            [-1, 1, 1],
            [-1, 1, -1],
            [-1, -1, 1],
            [-1, -1, -1]
        ])
    elif solid_type == 'octahedron':
        # Octahedron vertices
        points = np.array([
            [1, 0, 0],
            [-1, 0, 0],
            [0, 1, 0],
            [0, -1, 0],
            [0, 0, 1],
            [0, 0, -1]
        ])
    elif solid_type == 'dodecahedron':
        # Dodecahedron vertices
        phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        points = []
        for i in [-1, 1]:
            for j in [-1, 1]:
                points.extend([
                    [0, i/phi, j*phi],
                    [i/phi, j*phi, 0],
                    [i*phi, 0, j/phi]
                ])
        points = np.array(points)
    elif solid_type == 'icosahedron':
        # Icosahedron vertices
        phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        points = []
        for i in [-1, 1]:
            for j in [-1, 1]:
                points.append([0, i, j * phi])
                points.append([i, j * phi, 0])
                points.append([i * phi, 0, j])
        points = np.array(points)
    else:
        raise ValueError(f"Unsupported solid_type '{solid_type}'. Supported types are 'tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron'.")

    # Normalize and scale points to the sphere
    norms = np.linalg.norm(points, axis=1)
    points = points / norms[:, np.newaxis]  # Normalize vectors
    points *= radius  # Scale to the sphere radius

    # Convert to spherical coordinates
    nodes = []
    for idx, (x, y, z) in enumerate(points):
        latitude = math.degrees(math.asin(z / radius))
        longitude = math.degrees(math.atan2(y, x))
        node = {
            "id": f"node_{idx:03}",
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "category": "major_node",
            "associated_ley_lines": [],
            "nearby_nodes": []
        }
        nodes.append(node)
    logging.info(f"Generated {len(nodes)} nodes for solid {solid_type}.")
    return nodes

def connect_nodes(nodes: list, radius: float, max_distance: float, auto_adjust: bool = False) -> tuple:
    """
    Connect nodes within a certain distance to create ley lines.

    Args:
        nodes (list): List of node dictionaries.
        radius (float): Radius of the sphere in kilometers.
        max_distance (float): Maximum distance between nodes to create a ley line.
        auto_adjust (bool): Whether to automatically adjust distance parameters if no connections are made.

    Returns:
        tuple: (list, dict) - (ley_lines, metadata) where metadata includes suggestions and adjustments,
               connection statistics, and parameter adjustments

    Raises:
        ValueError: If distance parameters are invalid.
    """
    logging.info(f"Connecting nodes within {max_distance} km to create ley lines.")
    
    # Get suggested parameters
    suggestions = suggest_distance_parameters(nodes)
    
    # Initialize metadata
    metadata = {
        'original_max_distance': max_distance,
        'suggested_parameters': suggestions,
        'adjustments_made': [],
        'connection_stats': {'attempted': 0, 'successful': 0}
    }

    # Calculate minimum practical distance based on node density
    node_count = len(nodes)
    density_factor = math.sqrt(node_count) / 10  # Adjust scaling based on number of nodes
    min_distance = (0.1 * radius) / density_factor
    
    # Validate and potentially adjust max_distance
    max_possible_distance = math.pi * radius
    if max_distance > max_possible_distance:
        max_distance = max_possible_distance
        metadata['adjustments_made'].append(
            f"Adjusted max_distance to sphere limit: {max_distance:.2f} km"
        )

    # Initialize connection tracking
    ley_lines = []
    ley_line_id = 0
    num_nodes = len(nodes)
    connections_made = False
    for i in range(num_nodes):
        node_a = nodes[i]
        for j in range(i + 1, num_nodes):
            node_b = nodes[j]

            try:
                # Calculate distance between nodes using the haversine formula
                lat1 = math.radians(node_a['coordinates']['latitude'])
                lon1 = math.radians(node_a['coordinates']['longitude'])
                lat2 = math.radians(node_b['coordinates']['latitude'])
                lon2 = math.radians(node_b['coordinates']['longitude'])
                
                # Use stable formula for small angles
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                
                # Use double-precision arithmetic for better accuracy
                sin_dlat = math.sin(dlat/2)
                sin_dlon = math.sin(dlon/2)
                cos_lat1 = math.cos(lat1)
                cos_lat2 = math.cos(lat2)
                
                # Calculate haversine formula components with validation
                a = sin_dlat**2 + cos_lat1 * cos_lat2 * sin_dlon**2
                
                # Handle numerical precision
                a = max(0.0, min(1.0, a))  # Clamp to [0, 1]
                
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                distance = radius * c
                
                # Log distances when debugging
                if distance > max_distance:
                    logging.debug(f"Distance between {node_a['id']} and {node_b['id']}: {distance:.2f} km (exceeds max_distance)")
                elif distance < min_distance:
                    logging.debug(f"Distance between {node_a['id']} and {node_b['id']}: {distance:.2f} km (below min_distance)")

            except (ValueError, ZeroDivisionError) as e:
                logging.warning(f"Error calculating distance between nodes {node_a['id']} and {node_b['id']}: {str(e)}")
                continue

            # Add connection if within valid range
            if min_distance <= distance <= max_distance:
                connections_made = True
                ley_line = {
                    "id": f"leyline_{ley_line_id:03}",
                    "nodes": [node_a['id'], node_b['id']],
                    "category": "primary" if node_a['category'] == "major_node" and node_b['category'] == "major_node" else "secondary"
                }
                ley_lines.append(ley_line)
                ley_line_id += 1
                node_a['associated_ley_lines'].append(ley_line['id'])
                node_b['associated_ley_lines'].append(ley_line['id'])
                if node_b['id'] not in node_a['nearby_nodes']:
                    node_a['nearby_nodes'].append(node_b['id'])
                if node_a['id'] not in node_b['nearby_nodes']:
                    node_b['nearby_nodes'].append(node_a['id'])
    if not connections_made:
        logging.warning("No ley lines were generated. This might indicate that the distance parameters need adjustment.")
    else:
        logging.info(f"Generated {len(ley_lines)} ley lines.")
    metadata['connection_stats']['attempted'] = num_nodes * (num_nodes - 1) // 2
    metadata['connection_stats']['successful'] = len(ley_lines)
    return ley_lines, metadata

def generate_nodes_and_ley_lines(
    solid_type: str = 'icosahedron',
    radius: float = 6371,
    max_distance: float = 5000,
    auto_adjust: bool = False
) -> dict:
    """
    Generate nodes and ley lines based on a Platonic solid mapping.

    Args:
        solid_type (str): Type of Platonic solid.
        radius (float): Radius of the sphere in kilometers.
        max_distance (float): Maximum distance between nodes to create ley lines.
        auto_adjust (bool): Whether to automatically adjust parameters for optimal connections.

    Returns:
        dict: Dictionary containing nodes, ley lines, and metadata including adjustments and statistics.
    """
    """
    Generate nodes and ley lines based on a Platonic solid mapping.

    Args:
        solid_type (str): Type of Platonic solid. Options are 'tetrahedron', 'cube',
                          'octahedron', 'dodecahedron', 'icosahedron'.
        radius (float): Radius of the sphere in kilometers.
        max_distance (float): Maximum distance between nodes to create ley lines.

    Returns:
        dict: Dictionary containing nodes and ley lines.

    Raises:
        ValueError: If inputs are invalid.
    """
    # Validate inputs
    valid_solids = ['tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron']
    if solid_type not in valid_solids:
        raise ValueError(f"Invalid solid_type '{solid_type}'. Must be one of {valid_solids}.")
    if radius <= 0:
        raise ValueError("Radius must be a positive number.")
    if max_distance <= 0:
        raise ValueError("Max distance must be a positive number.")

    try:
        # Generate initial nodes
        nodes = generate_platonic_solid(solid_type, radius)
        
        # Get parameter suggestions
        suggested_params = suggest_distance_parameters(nodes)
        
        # Adjust parameters if auto_adjust is enabled
        if auto_adjust:
            max_distance = min(max_distance, suggested_params['max_distance'])
            min_distance = suggested_params['min_distance']
        else:
            min_distance = 0  # Use original behavior if auto_adjust is disabled
        
        # Connect nodes with adjusted parameters
        ley_lines, metadata = connect_nodes(nodes, radius, max_distance, auto_adjust)
        
        # Update metadata with parameter information
        metadata['parameter_adjustments'] = {
            'original_max_distance': max_distance,
            'suggested_max_distance': suggested_params['max_distance'],
            'suggested_min_distance': suggested_params['min_distance'],
            'auto_adjust_enabled': auto_adjust,
            'final_max_distance': max_distance if not auto_adjust else min(max_distance, suggested_params['max_distance'])
        }
        
        data = {
            "nodes": nodes,
            "ley_lines": ley_lines,
            "metadata": metadata
        }
        return data
    except Exception as e:
        logging.exception("An error occurred during node and ley line generation.")
        raise

def save_to_file(data: dict, output_file: str):
    """
    Save data to a JSON file atomically to prevent data corruption.

    Args:
        data (dict): Data to be saved.
        output_file (str): Path to the output JSON file.

    Raises:
        IOError: If the file cannot be written.
    """
    temp_file = output_file + '.tmp'
    try:
        with open(temp_file, "w") as file:
            json.dump(data, file, indent=4)
        os.replace(temp_file, output_file)
        logging.info(f"JSON data saved to {output_file}.")
    except Exception as e:
        logging.exception(f"Failed to save JSON data to {output_file}.")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise

# Example usage
if __name__ == "__main__":
    try:
        # Generate multiple ley line configurations
        solids = ['tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron']
        for solid in solids:
            output_file = f"ley_lines_{solid}.json"
            data = generate_nodes_and_ley_lines(solid_type=solid, radius=6371, max_distance=5000)
            save_to_file(data, output_file)
        logging.info("Ley line generation completed successfully for all solids.")
    except Exception as error:
        logging.exception("An unexpected error occurred in the main execution.")
