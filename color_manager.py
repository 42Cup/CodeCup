import colorsys

def start_color_drag(event, target, globals_dict):
    globals_dict['left_pressed'] = event.num == 1 if not globals_dict.get('right_pressed') else globals_dict['left_pressed']
    globals_dict['right_pressed'] = event.num == 3 if not globals_dict.get('left_pressed') else globals_dict['right_pressed']
    if globals_dict['left_pressed'] and globals_dict['right_pressed']:
        # Double-drag disabled
        return
    elif globals_dict['left_right_drag_active']:
        return
    
    if not globals_dict.get('left_right_drag_active'):
        globals_dict['start_x'] = event.x_root
        globals_dict['start_y'] = event.y_root
    globals_dict['color_target'] = target
    current_color = {'font': globals_dict['font_color'], 'list_bg': globals_dict['list_bg_color'],
                     'frame_bg': globals_dict['frame_bg_color'], 'list_item_bg': globals_dict['list_item_bg_color']}[target]
    r, g, b = [int(current_color[i:i+2], 16)/255 for i in (1, 3, 5)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    globals_dict['start_hue'], globals_dict['start_sat'], globals_dict['start_light'] = h, s, l

def apply_color(target, color, text_editor, entry, treeview, style, globals_dict):
    frames = [globals_dict['root'], globals_dict['left_frame'], globals_dict['right_frame'],
              globals_dict['entry_frame'], globals_dict['button_frame'], globals_dict['editor_frame']]
    configs = {
        'font': lambda: (text_editor.config(fg=color), entry.config(fg=color), 
                         treeview.config(style="Custom.Treeview"), style.configure("Custom.Treeview", foreground=color)),
        'list_bg': lambda: (treeview.config(style="Custom.Treeview"), 
                           style.configure("Custom.Treeview", background=color, fieldbackground=color), 
                           text_editor.config(bg=color), entry.config(bg=color),
                           globals_dict['list_bg_color'] == globals_dict['list_item_bg_color'] or setattr(globals_dict, 'list_item_bg_color', color)),
        'frame_bg': lambda: [frame.config(bg=color) for frame in frames],
        'list_item_bg': lambda: None  # Deprecated since merged with list_bg
    }
    config_action = configs.get(target)
    if config_action:
        config_action()

def apply_initial_colors(text_editor, entry, treeview, style, globals_dict):
    """Apply all stored colors on application launch."""
    apply_color('font', globals_dict['font_color'], text_editor, entry, treeview, style, globals_dict)
    apply_color('list_bg', globals_dict['list_bg_color'], text_editor, entry, treeview, style, globals_dict)
    apply_color('frame_bg', globals_dict['frame_bg_color'], text_editor, entry, treeview, style, globals_dict)
        
def update_color(event, text_editor, entry, treeview, style, globals_dict):
    if 'start_hue' not in globals_dict or globals_dict['start_x'] is None or globals_dict['color_target'] is None:
        return
    dx, dy = event.x_root - globals_dict['start_x'], event.y_root - globals_dict['start_y']
    hue = (globals_dict['start_hue'] + (dx / 200.0)) % 1.0
    sat = max(0.0, min(1.0, globals_dict['start_sat'] + (dy / -200.0)))
    light = max(0.2, min(0.8, globals_dict['start_light'] + (dy / -400.0)))
    r, g, b = colorsys.hls_to_rgb(hue, light, sat)
    color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
    if globals_dict['color_target'] == 'list_bg':
        globals_dict['list_bg_color'] = color
        globals_dict['list_item_bg_color'] = color  # Sync both zones
    elif globals_dict['color_target'] == 'font':
        globals_dict['font_color'] = color  # Update font_color for consistency
    else:
        globals_dict[{'frame_bg': 'frame_bg_color'}[globals_dict['color_target']]] = color
    apply_color(globals_dict['color_target'], color, text_editor, entry, treeview, style, globals_dict)


