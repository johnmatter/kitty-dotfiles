"""Custom tab bar with theme-aware colors and auto-width"""
# pyright: reportMissingImports=false

from kitty.fast_data_types import Screen, get_boss, get_options
from kitty.tab_bar import (DrawData, ExtraData, TabBarData, as_rgb,
                           draw_title)
from kitty.utils import color_as_int

opts = get_options()

# Colors to cycle through for inactive tabs (color1-color5)
INACTIVE_TAB_COLORS = ['color1', 'color2', 'color3', 'color4', 'color5']

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
    """Draw tab with theme-aware colors and auto-width"""
    # Calculate auto-width
    try:
        ntabs = len(get_boss().active_tab_manager.tabs)
        if ntabs > 0:
            # Calculate width per tab
            available_width = screen.cols - (ntabs - 1)  # Account for separators
            width_per_tab = available_width // ntabs
            # Give extra width to first few tabs if there's remainder
            if index < (available_width % ntabs):
                width_per_tab += 1
            max_title_length = max(10, width_per_tab)
    except:
        pass  # Use original max_title_length if calculation fails

    if draw_data.leading_spaces:
        screen.draw(" " * draw_data.leading_spaces)
    
    # Set colors based on tab state
    if tab.is_active:
        # Active tab: inverted colors - background color for text, foreground color for background
        screen.cursor.bg = as_rgb(color_as_int(_get_theme_color('foreground')))
        screen.cursor.fg = as_rgb(color_as_int(_get_theme_color('background')))
    else:
        # Inactive tab: cycle through color1-color5 background, color0 text
        color_index = index % len(INACTIVE_TAB_COLORS)
        bg_color_name = INACTIVE_TAB_COLORS[color_index]
        screen.cursor.bg = as_rgb(color_as_int(_get_theme_color(bg_color_name)))
        screen.cursor.fg = as_rgb(color_as_int(_get_theme_color('color0')))
    
    # Draw the tab title with center justification
    title = tab.title
    available_width = max_title_length - 4  # Account for padding (2 spaces on each side)
    
    if len(title) > available_width:
        title = title[:available_width-1] + "…"
    
    # Center the title within the available width
    title_width = len(title)
    total_padding = available_width - title_width
    left_padding = total_padding // 2
    right_padding = total_padding - left_padding
    
    # Draw the centered title with padding
    screen.draw(" " * (2 + left_padding))  # 2 base spaces + left padding
    screen.draw(title)
    screen.draw(" " * (2 + right_padding))  # 2 base spaces + right padding
    
    # Fill remaining space to achieve auto-width
    current_width = screen.cursor.x - before
    remaining_width = max_title_length - current_width
    if remaining_width > 0:
        screen.draw(" " * remaining_width)
    
    # Handle trailing spaces and overflow
    trailing_spaces = min(max_title_length - 1, draw_data.trailing_spaces)
    max_title_length -= trailing_spaces
    extra = screen.cursor.x - before - max_title_length
    if extra > 0:
        screen.cursor.x -= extra + 1
        screen.draw("…")
    
    if trailing_spaces:
        screen.draw(" " * trailing_spaces)
    
    screen.cursor.bold = screen.cursor.italic = False
    
    # Draw separator
    if not is_last:
        screen.cursor.fg = as_rgb(color_as_int(_get_theme_color('color8')))
        screen.cursor.bg = as_rgb(color_as_int(_get_theme_color('background')))
        screen.draw(draw_data.sep)
    
    # Reset colors
    screen.cursor.fg = 0
    screen.cursor.bg = 0
    return screen.cursor.x 