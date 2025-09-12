"""Custom tab bar with wiki tab on the right side"""
# pyright: reportMissingImports=false

from kitty.fast_data_types import Screen, get_options
from kitty.tab_bar import (DrawData, ExtraData, TabBarData, as_rgb,
                           draw_title)
from kitty.utils import color_as_int

opts = get_options()

# Tab Color Configuration
# Maps tab elements to specific theme colors
# Available colors: background, foreground, cursor, selection_background, selection_foreground
# color0-color15 (standard ANSI colors), or any custom colors defined in your theme
TAB_COLORS = {
    'active_tab': {
        'fg': 'foreground',        # Active tab text color
        'bg': 'color8',            # Active tab background (bright black)
    },
    'inactive_tab': {
        'fg': 'color7',            # Inactive tab text color (light gray)
        'bg': 'background',        # Inactive tab background
    },
    'active_tab_hover': {
        'fg': 'foreground',        # Active tab text when hovered
        'bg': 'color10',           # Active tab background when hovered (bright green)
    },
    'inactive_tab_hover': {
        'fg': 'color15',           # Inactive tab text when hovered (bright white)
        'bg': 'color8',            # Inactive tab background when hovered
    },
    'tab_separator': {
        'fg': 'color8',            # Tab separator color
        'bg': 'background',        # Tab separator background
    },
    'wiki_tab': {
        'fg': 'color3',            # Wiki tab text color (yellow)
        'bg': 'color5',            # Wiki tab background (magenta)
    }
}

def _get_theme_color(color_name: str) -> int:
    """Get a color value from the current kitty theme"""
    try:
        # Get color from kitty's options
        if hasattr(opts, color_name):
            return getattr(opts, color_name)
        # Handle numbered colors (color0-color15)
        if color_name.startswith('color') and color_name[5:].isdigit():
            color_num = int(color_name[5:])
            if 0 <= color_num <= 15:
                return getattr(opts, color_name)
        # Fallback to a safe default
        return opts.foreground
    except (AttributeError, ValueError):
        # If color doesn't exist, fallback to foreground
        return opts.foreground

def _apply_tab_colors(screen: Screen, tab_type: str, element: str = 'fg'):
    """Apply configured colors to screen cursor"""
    if tab_type in TAB_COLORS:
        color_name = TAB_COLORS[tab_type].get(element)
        if color_name:
            color_value = _get_theme_color(color_name)
            if element == 'fg':
                screen.cursor.fg = as_rgb(color_as_int(color_value))
            elif element == 'bg':
                screen.cursor.bg = as_rgb(color_as_int(color_value))

def _draw_left_status(
    draw_data: DrawData,
    screen: Screen,
    tab: TabBarData,
    before: int,
    max_title_length: int,
    index: int,
    is_last: bool,
    extra_data: ExtraData,
) -> int:
    """Draw regular tabs on the left, wiki tab on the right"""
    if draw_data.leading_spaces:
        screen.draw(" " * draw_data.leading_spaces)
    
    # Wiki tab gets drawn on the right side
    wiki_tab_length = 6  # Length of " wiki "
    if tab.title != 'wiki':
        # Draw regular tab with configured colors
        tab_type = 'active_tab' if tab.is_active else 'inactive_tab'
        _apply_tab_colors(screen, tab_type, 'fg')
        _apply_tab_colors(screen, tab_type, 'bg')
        draw_title(draw_data, screen, tab, index)
    else:
        # Draw wiki tab on the right side with special colors
        save_x = screen.cursor.x
        screen.cursor.x = screen.columns - wiki_tab_length
        _apply_tab_colors(screen, 'wiki_tab', 'fg')
        _apply_tab_colors(screen, 'wiki_tab', 'bg')
        draw_title(draw_data, screen, tab, index)
        screen.cursor.x = save_x
    
    trailing_spaces = min(max_title_length - 1, draw_data.trailing_spaces)
    max_title_length -= trailing_spaces
    extra = screen.cursor.x - before - max_title_length
    if extra > 0:
        screen.cursor.x -= extra + 1
        screen.draw("…")
    
    if trailing_spaces:
        screen.draw(" " * trailing_spaces)
    
    screen.cursor.bold = screen.cursor.italic = False
    
    # Apply separator colors
    if not is_last:
        _apply_tab_colors(screen, 'tab_separator', 'fg')
        _apply_tab_colors(screen, 'tab_separator', 'bg')
        screen.draw(draw_data.sep)
    
    # Reset colors
    screen.cursor.fg = 0
    screen.cursor.bg = 0
    return screen.cursor.x

def draw_tab(
    draw_data: DrawData,
    screen: Screen,
    tab: TabBarData,
    before: int,
    max_title_length: int,
    index: int,
    is_last: bool,
    extra_data: ExtraData,
) -> int:
    """Main draw function"""
    # Draw the tab (wiki tab will be positioned on the right automatically)
    end = _draw_left_status(
        draw_data, screen, tab, before, max_title_length, 
        index, is_last, extra_data
    )
    
    return end 