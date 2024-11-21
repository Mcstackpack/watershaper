import scipy.optimize as opt
import math
import streamlit as st

# Existing functions for the ellipsoid and volume/surface area calculations
def ellipsoid_surface_area_one_side(a, b, c):
    """Approximate curved surface area of one side of a half-ellipsoid (without base)."""
    p = 1.6075
    surface_area = 2 * math.pi * (((a * b)**p + (a * c)**p + (b * c)**p) / 3)**(1 / p)
    return surface_area

def ellipsoid_volume(a, b, c):
    """Calculate volume of a half-ellipsoid."""
    return (2 / 3) * math.pi * a * b * c

def objective(params, min_surface_area, c, min_volume):
    """Objective function for optimization, focusing on minimizing the difference in volume and surface area."""
    a, b = params  # Width and length
    surface_area = ellipsoid_surface_area_one_side(a, b, c)
    volume = ellipsoid_volume(a, b, c)
    
    # Penalize based on how far the calculated volume and surface area are from the minimum requirements
    surface_area_diff = abs(surface_area - min_surface_area)  
    volume_diff = abs(volume - min_volume)  # Minimize volume difference
    return surface_area_diff + volume_diff  # Objective: minimize both differences

def calculate_ellipsoid(min_surface_area, min_volume, depth):
    """Calculate width and length for the given constraints."""
    c = depth  # Depth corresponds to the semi-minor axis
    initial_guess = [min_surface_area / 100, min_surface_area / 80]  # Dynamic initial guess based on surface area

    # Constraints: volume and surface area
    constraints = [
        {"type": "ineq", "fun": lambda params: ellipsoid_volume(params[0], params[1], c) - min_volume},  # Volume >= min_volume
        {"type": "ineq", "fun": lambda params: params[1] - 1.5 * params[0]}  # b >= 1.5 * a
    ]

    # Bounds for width and length
    bounds = [(0.1, 100), (0.1, 100)]  # Allowable range for width (a) and length (b)

    # Perform optimization
    result = opt.minimize(
        objective,
        initial_guess,
        args=(min_surface_area, c, min_volume),
        bounds=bounds,
        constraints=constraints
    )

    if result.success:
        a, b = result.x
        return a, b, c
    else:
        return None, None, None

# Updated infiltration ditch function with corrections for trapezoidal cross-section
def calculate_infiltration_ditch(width, depth, min_volume, min_surface_area, roof_area):
    """
    Calculate volume and surface area for an infiltration ditch with trapezoidal cross-section,
    considering minimum volume and surface area requirements.
    """
    # Start by calculating the length such that the minimum volume is met
    length = min_volume / ((width * 0.5 + width) / 2 * depth)  # Adjust length to match minimum volume
    
    # Now that we have the length based on volume, we can calculate the surface area
    base_width = width * 0.5  # Base width is half the top width
    slant_height = math.sqrt((width - base_width)**2 / 4 + depth**2)  # Slant height from top to base

     # Function to calculate surface area based on length
    def calculate_surface_area(length):
        base_area = base_width * length  # Bottom area
        top_area = width * length  # Top area
        slanted_wall_area = slant_height * length  # One slanted wall
        return 2 * slanted_wall_area  # two slanted walls

    # Check if the surface area is below the minimum and adjust length accordingly
    current_surface_area = calculate_surface_area(length)
    
    # If the surface area is smaller than the minimum required, increase the length
    if current_surface_area < min_surface_area:
        # Scale the length to match the minimum surface area by proportion
        scale_factor = min_surface_area / current_surface_area
        length *= scale_factor

    # Calculate the final volume and surface area based on adjusted length
    volume = ((base_width + width) / 2) * depth * length
    surface_area = calculate_surface_area(length)
    
    # Return the volume, surface area, and adjusted length
    return volume, surface_area, length

# Streamlit UI setup
st.set_page_config(page_title="Watershaper", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
        .title { text-align: center; color: #1E2A47; }
        .subtitle { text-align: center; color: #1F75FE; margin-bottom: 30px; }
        .small-text { font-size: 16px; color: #333333; margin-bottom: 15px; }
        .result-container { background-color: #F2F2F2; padding: 20px; border-radius: 10px; }
        .stButton button { border-radius: 5px; padding: 10px; margin-top: 40px; }
        .stButton button:hover { background-color: #6CC6FF; border: 2px solid #1F75FE; }
        @media (max-width: 768px) {
            .center-buttons { text-align: left; }
        }
        @media (min-width: 769px) {
            .center-buttons { text-align: center; }
        }
    </style>
""", unsafe_allow_html=True)

# Display the logo at the top (smaller size)
st.markdown("""
    <div style="text-align: center;">
        <img src="https://dndexaqt.be/wp-content/uploads/2022/12/mainlogo.png" width="100">
    </div>
""", unsafe_allow_html=True)

# Title and description
st.markdown("<h1 class='title'>Watershaper</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Bereken de minimum vereisten en afmetingen voor bovengrondse infiltratie en regenputten volgens de GSV van 2023.</p>", unsafe_allow_html=True)

# Sidebar for inputs
with st.sidebar:
    st.header("Parameters")
    roof_square_meters = st.number_input('Horizontaal Dakoppervlak (m²):', min_value=0.0, value=50.0, step=0.1)
    has_rainwell = st.checkbox('Regenput met hergebruik aanwezig (-30 m²)', value=False)
    depth = st.slider('Diepte infiltratiegracht (m):', min_value=0.3, max_value=1.0, value=0.5, step=0.1)

# Calculate minimum volume and surface area for ellipsoid
min_volume = (roof_square_meters * 33) / 1000  # Convert to cubic meters
min_surface_area = roof_square_meters * 0.08  # Surface area in square meters

# Adjust roof square meters based on rainwell
if has_rainwell:
    roof_square_meters -= 30
    st.sidebar.markdown(f"### Adjusted Roof Square Meters: {roof_square_meters:.2f} m²")

# Display calculated minimum values
st.markdown(f"### Min Volume: {min_volume:.2f} m³")
st.markdown(f"### Min infiltratie oppervlakte: {min_surface_area:.2f} m²")

# Display the Rainwell minimum size message
if roof_square_meters < 80:
    st.subheader ("**Regenput dimensionering:** 5000l")
elif 80 <= roof_square_meters < 120:
    st.subheader("**Regenput dimensionering:** 7500l")
elif 120 <= roof_square_meters < 200:
    st.subheader("**Regenput dimensionering:** 10000l")
else:
    rainwell_size = roof_square_meters * 100  # 100l per square meter
    st.subheader(f"**Regenput dimensionering:** {rainwell_size:.0f}l")

# Initialize session state for storing results if they don't already exist
if 'results' not in st.session_state:
    st.session_state.results = []

# Buttons to trigger calculations
col1, col2, col3 = st.columns(3)
with col1:
    if st.button('Bereken Infiltratiekom'):
        with st.spinner('Calculating...'):
            width, length, depth = calculate_ellipsoid(min_surface_area, min_volume, 0.3)
            if width is not None and length is not None:
                diameter_width = width * 2
                diameter_length = length * 2
                final_surface_area = ellipsoid_surface_area_one_side(width, length, depth)
                final_volume = ellipsoid_volume(width, length, depth)

                with st.container():
                    st.subheader("Resultaat:")
                    st.write(f"**Breedte:** {diameter_width:.2f} m")
                    st.write(f"**Lengte:** {diameter_length:.2f} m")
                    st.write(f"**Diepte:** {depth:.2f} m")
                    st.write(f"**Verhouding:** {diameter_length / diameter_width:.2f}")
                    st.write(f"**Infiltratie oppervlakte:** {final_surface_area:.2f} m²")
                    st.write(f"**Volume:** {final_volume:.2f} m³")
                    if final_volume < min_volume:
                        st.warning("Opgelet: Volume zit onder gevraagde hoeveelheid.")
                    else:
                        st.success("Volume zit boven of is gelijk aan gevraagde hoeveelheid.")
            else:
                st.error('Error, controleer parameters')

with col2:
    if st.button('Bereken Wadi'):
        with st.spinner('Calculating...'):
            width, length, depth = calculate_ellipsoid(min_surface_area, min_volume, 0.5)
            if width is not None and length is not None:
                diameter_width = width * 2
                diameter_length = length * 2
                final_surface_area = ellipsoid_surface_area_one_side(width, length, depth)
                final_volume = ellipsoid_volume(width, length, depth)

                with st.container():
                    st.subheader("Resultaat:")
                    st.write(f"**Breedte:** {diameter_width:.2f} m")
                    st.write(f"**Lengte:** {diameter_length:.2f} m")
                    st.write(f"**Diepte:** {depth:.2f} m")
                    st.write(f"**Verhouding:** {diameter_length / diameter_width:.2f}")
                    st.write(f"**Infiltratie oppervlakte:** {final_surface_area:.2f} m²")
                    st.write(f"**Volume:** {final_volume:.2f} m³")
                    if final_volume < min_volume:
                        st.warning("Opgelet: Volume zit onder gevraagde hoeveelheid.")
                    else:
                        st.success("Volume zit boven of is gelijk aan gevraagde hoeveelheid.")
            else:
                st.error('Error, controleer parameters')

with col3:
    if st.button('Bereken Infiltratiegracht'):
        with st.spinner('Calculating...'):
            width = 1.5  # Standard ditch width
            volume, surface_area, length = calculate_infiltration_ditch(width, depth, min_volume, min_surface_area, roof_square_meters)
            # Display results for Infiltration Ditch
            with st.container():
                st.subheader("Resultaat")
                st.write(f"**Breedte:** {width:.2f} m")
                st.write(f"**Lengte:** {length:.2f} m")
                st.write(f"**Diepte:** {depth:.2f} m")
                st.write(f"**Infiltratie oppervlakte** {surface_area:.2f} m²")
                st.write(f"**Volume:** {volume:.2f} m³")
                if volume < min_volume:
                        st.warning("Opgelet: Volume zit onder gevraagde hoeveelheid.")
                else:
                        st.success("Volume zit boven of is gelijk aan gevraagde hoeveelheid.")
                
                
                
