import streamlit as st
import math
import scipy.optimize as opt

def ellipsoid_surface_area_one_side(a, b, c):
    """Approximate curved surface area of one side of a half-ellipsoid (without base)."""
    p = 1.6075
    surface_area = 2 * math.pi * (((a * b)**p + (a * c)**p + (b * c)**p) / 3)**(1 / p)
    return surface_area

def ellipsoid_volume(a, b, c):
    """Calculate volume of a half-ellipsoid."""
    return (2 / 3) * math.pi * a * b * c

def objective(params, min_surface_area, min_volume, c):
    """Objective function for optimization."""
    a, b = params  # Width and length
    surface_area = ellipsoid_surface_area_one_side(a, b, c)
    volume = ellipsoid_volume(a, b, c)

    # Penalize if constraints are not met
    penalty = 0
    if surface_area < min_surface_area:
        penalty += (min_surface_area - surface_area)**2
    if volume < min_volume:
        penalty += (min_volume - volume)**2

    # Minimize the penalty and total dimensions (compactness)
    return penalty + a + b

def calculate_ellipsoid(min_surface_area, min_volume, depth):
    """Calculate width and length for the given constraints."""
    c = depth  # Depth corresponds to the semi-minor axis
    initial_guess = [0.5, 1.0]  # Initial guess

    # Set more restrictive bounds
    result = opt.minimize(
        objective,
        initial_guess,
        args=(min_surface_area, min_volume, c),
        bounds=[(0.1, 5), (0.1, 5)],  # Restrict width and length to smaller ranges
    )

    if result.success:
        a, b = result.x
        return a, b
    else:
        return None, None

# Streamlit UI
st.title('Half-Ellipsoid Calculator')

min_surface_area = st.number_input('Minimum Surface Area (m²):', min_value=0.0, value=8.0)
min_volume = st.number_input('Minimum Volume (m³):', min_value=0.0, value=3.3)
depth = st.number_input('Depth (m):', min_value=0.0, value=0.3)

if st.button('Calculate'):
    width, length = calculate_ellipsoid(min_surface_area, min_volume, depth)
    if width is not None and length is not None:
        st.write(f'Calculated width: {width:.2f} m')
        st.write(f'Calculated length: {length:.2f} m')
    else:
        st.error('Optimization failed. Check the input values.')
