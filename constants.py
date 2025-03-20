# Define the toggle size as an easily editable constant
TOGGLE_GEOMETRY = "75x50"

GLOBAL_DEFAULTS = {
    'font_color': "#000000",
    'list_bg_color': "#f0f0f0",
    'frame_bg_color': "#ffffff",
    'list_item_bg_color': "#ffffff",
    'font_size': 10,
    'start_x': None,
    'start_y': None,
    'start_hue': None,
    'start_sat': None,
    'start_light': None,
    'color_target': None,
    'left_pressed': False,
    'right_pressed': False,
    'left_right_drag_active': False,
    # Added to track toggle state and store normal geometry
    'is_toggled': False,
    'normal_geometry': None,
}