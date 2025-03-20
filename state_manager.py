from logic import load_state, save_state
from color_manager import apply_color  # Import apply_color





def set_initial_state(globals_dict):
    sash_pos, url, width, height, x, y, globals_dict['font_color'], globals_dict['list_bg_color'], \
    globals_dict['frame_bg_color'], globals_dict['list_item_bg_color'], globals_dict['font_size'] = load_state()
    if x is None or y is None:
        globals_dict['root'].update_idletasks()
        screen_width = globals_dict['root'].winfo_screenwidth()
        screen_height = globals_dict['root'].winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
    globals_dict['root'].geometry(f"{width}x{height}+{x}+{y}")
    globals_dict['root'].update_idletasks()  # Ensure geometry is applied before setting sash
    globals_dict['main_paned'].sash_place(0, sash_pos, 0)
    globals_dict['entry'].delete(0, 'end')
    globals_dict['entry'].insert(0, url)
    if url:
        from logic import update_treeview
        update_treeview(globals_dict['entry'], globals_dict['treeview'])
    from logic import show_gh_auth_status, on_treeview_select
    auth_status = show_gh_auth_status(globals_dict['text_editor'])
    current_branch = on_treeview_select(globals_dict['entry'], globals_dict['treeview'], 
                                      globals_dict['text_editor'], globals_dict['auth_label'])
    globals_dict['auth_label'].config(text=f"● {current_branch if current_branch else 'No branch'} - {auth_status}", fg="#FF0000")
    globals_dict['auth_label'].config(fg="#000000")  # Reset to black 
    # Use apply_color to set all colors consistently
    apply_color('font', globals_dict['font_color'], globals_dict['text_editor'], 
                globals_dict['entry'], globals_dict['treeview'], globals_dict['style'], globals_dict)
    apply_color('list_bg', globals_dict['list_bg_color'], globals_dict['text_editor'], 
                globals_dict['entry'], globals_dict['treeview'], globals_dict['style'], globals_dict)
    apply_color('frame_bg', globals_dict['frame_bg_color'], globals_dict['text_editor'], 
                globals_dict['entry'], globals_dict['treeview'], globals_dict['style'], globals_dict)
    globals_dict['text_editor'].config(font=("Courier", globals_dict['font_size']))

def on_close(globals_dict):
    save_current_state(globals_dict)
    globals_dict['root'].destroy()

def save_current_state(globals_dict):
    sash_pos = globals_dict['main_paned'].sash_coord(0)[0]
    url = globals_dict['entry'].get().strip()
    width = globals_dict['root'].winfo_width()
    height = globals_dict['root'].winfo_height()
    x = globals_dict['root'].winfo_x()
    y = globals_dict['root'].winfo_y()
    save_state(sash_pos, url, width, height, x, y, globals_dict['font_color'], 
               globals_dict['list_bg_color'], globals_dict['frame_bg_color'], 
               globals_dict['list_item_bg_color'], globals_dict['font_size'])