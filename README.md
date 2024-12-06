# Ley Line Network Generator

A development tool for generating and visualizing ley line networks, featuring a Streamlit-based user interface with interactive 3D visualization powered by Plotly. The application provides network parameter controls, statistical analysis, and preset management functionality for saving and loading network configurations.

![Banner](banner.png)

## Features

- Interactive 3D visualization of ley line networks using Plotly
- Support for multiple Platonic solid base structures:
  - Tetrahedron (4 vertices)
  - Cube (8 vertices)
  - Octahedron (6 vertices)
  - Dodecahedron (12 vertices)
  - Icosahedron (12 vertices)
- Parameter controls for network generation:
  - Sphere radius customization
  - Maximum connection distance settings
  - Auto-adjustment of parameters
- Preset management:
  - Save custom configurations
  - Load existing presets
  - Delete unused presets
- Batch generation capabilities:
  - Generate multiple configurations simultaneously
  - Compare network statistics
  - Export results in JSON and CSV formats
- Network statistics and analysis:
  - Node counts and distributions
  - Connection success rates
  - Network density metrics
- Reference point visualization:
  - Custom latitude/longitude inputs
  - Visual markers and grid lines

## Installation

### macOS Installation Guide

#### Prerequisites
1. Install Python 3.8 or later:
   - Using Homebrew (recommended):
     ```bash
     brew install python@3.11
     ```
   - Or download from [Python.org](https://www.python.org/downloads/macos/)

2. Install pip (if not included with Python):
   ```bash
   curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
   python3 get-pip.py
   ```

#### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://replit.com/@username/ley-line-generator
   cd ley-line-generator
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   python3 -m pip install streamlit plotly numpy pandas
   ```

4. Configure Streamlit:
   Create `.streamlit/config.toml` file:
   ```bash
   mkdir -p .streamlit
   ```
   Add the following content to `.streamlit/config.toml`:
   ```toml
   [server]
   headless = true
   address = "0.0.0.0"
   port = 5000

   [theme]
   base = "dark"
   primaryColor = "#FF4B4B"
   backgroundColor = "#0E1117"
   secondaryBackgroundColor = "#262730"
   ```

#### Running the Application
1. Start the application:
   ```bash
   streamlit run main.py
   ```

2. Access the web interface at `http://localhost:5000`

#### Troubleshooting
1. **Permission Issues**:
   - If you encounter permission errors during installation:
     ```bash
     sudo chown -R $(whoami) $(brew --prefix)/*
     ```

2. **Python Path Issues**:
   - If Python is not found, add it to your PATH:
     ```bash
     echo 'export PATH="/usr/local/opt/python/libexec/bin:$PATH"' >> ~/.zshrc
     source ~/.zshrc
     ```

3. **Port Already in Use**:
   - If port 5000 is already in use:
     ```bash
     # Check what's using the port
     lsof -i :5000
     # Use a different port
     streamlit run main.py --server.port 8501
     ```

4. **Dependency Conflicts**:
   - If you encounter dependency conflicts:
     ```bash
     pip install --upgrade pip
     pip install -r requirements.txt --force-reinstall
     ```

## Usage

1. Start the application:
```bash
streamlit run main.py
```

2. Access the web interface at `http://localhost:5000`

3. Configure network parameters:
   - Select a Platonic solid type
   - Set the sphere radius (in kilometers)
   - Adjust the maximum ley line distance
   - Enable/disable auto-adjustment

4. Use presets:
   - Select from existing presets
   - Save new configurations
   - Delete unused presets

5. Generate batch configurations:
   - Select multiple solid types
   - Set common parameters
   - Generate and compare results

## Parameter Explanations

### Solid Type
- **Tetrahedron**: 4 vertices, suitable for minimal networks
- **Cube**: 8 vertices, good for balanced coverage
- **Octahedron**: 6 vertices, optimal for medium-sized networks
- **Dodecahedron**: 12 vertices, high density coverage
- **Icosahedron**: 12 vertices, most uniform distribution

### Radius
- Default: 6371 km (Earth's radius)
- Range: 1-10000 km
- Affects: Overall network scale and node distribution

### Maximum Distance
- Controls the maximum length of ley lines
- Affects connection density and network coverage
- Auto-adjustment available for optimal results

## Example Configurations

### Earth-scale Network
```json
{
    "solid_type": "icosahedron",
    "radius": 6371,
    "max_distance": 5000
}
```

### Compact Network
```json
{
    "solid_type": "octahedron",
    "radius": 1000,
    "max_distance": 800
}
```

### Dense Network
```json
{
    "solid_type": "dodecahedron",
    "radius": 2000,
    "max_distance": 2000
}
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
