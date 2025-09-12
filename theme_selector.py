#!/usr/bin/env .venv/bin/python

import os
import re
from pathlib import Path
from blessed import Terminal

def parse_theme_colors(theme_file):
  """Parse colors from a kitty theme file."""
  colors = {}
  try:
    with open(theme_file, 'r') as f:
      for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
          match = re.match(r'(\w+)\s+#([0-9a-fA-F]{6})', line)
          if match:
            colors[match.group(1)] = match.group(2)
  except Exception:
    pass
  return colors

def get_themes():
  """Get all theme files from the themes directory."""
  themes_dir = Path("kitty-themes/themes")
  if not themes_dir.exists():
    return []
  
  themes = []
  for theme_file in themes_dir.glob("*.conf"):
    colors = parse_theme_colors(theme_file)
    if colors:
      themes.append((theme_file.stem, theme_file, colors))
  
  return sorted(themes)

def apply_theme(theme_file):
  """Apply the selected theme by updating the symlink."""
  theme_path = f"./kitty-themes/themes/{theme_file.name}"
  try:
    if os.path.exists("theme.conf"):
      os.remove("theme.conf")
    os.symlink(theme_path, "theme.conf")
    return True
  except Exception:
    return False

def hex_to_rgb(hex_color):
  """Convert hex color to RGB tuple."""
  try:
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
  except (ValueError, IndexError):
    return 128, 128, 128  # Default gray

def create_shell_preview(term, colors, start_y, width):
  """Create a realistic shell session preview."""
  lines = []
  
  # Color mapping from kitty ANSI to shell elements
  color_map = {
    'prompt': colors.get('color2', '50fa7b'),      # green for prompt
    'command': colors.get('color5', 'bd92f8'),     # magenta for commands
    'string': colors.get('color2', '50fa7b'),      # green for strings
    'comment': colors.get('color3', 'f0fa8b'),     # yellow for comments
    'error': colors.get('color1', 'ff5555'),       # red for errors
    'param': colors.get('color4', 'bd92f8'),       # blue for parameters
    'operator': colors.get('color6', '8ae9fc'),    # cyan for operators
    'number': colors.get('color3', 'f0fa8b'),      # yellow for numbers
    'normal': colors.get('foreground', 'f8f8f2'),  # normal text
    'bg': colors.get('background', '1e1f28')       # background
  }
  
  # Mock shell session
  shell_lines = [
    ("❯ ", 'prompt', "git status", 'command'),
    ("On branch ", 'normal', "main", 'param'),
    ("Your branch is up to date with ", 'normal', "'origin/main'", 'string'),
    ("", 'normal'),
    ("❯ ", 'prompt', "ls -la ", 'command', "*.py", 'param'),
    ("theme_selector.py", 'normal', "  ", 'normal', "# Theme selector script", 'comment'),
    ("config.py", 'normal', "         ", 'normal', "# Configuration file", 'comment'),
    ("", 'normal'),
    ("❯ ", 'prompt', "python -c ", 'command', '"print(', 'operator', '"Hello World!"', 'string', ')"', 'operator'),
    ("Hello World!", 'normal'),
    ("", 'normal'),
    ("❯ ", 'prompt', "make build", 'command'),
    ("Building project...", 'normal'),
    ("✓ ", 'normal', "Compilation successful", 'normal'),
    ("", 'normal'),
    ("❯ ", 'prompt', "cat /nonexistent", 'command'),
    ("cat: /nonexistent: No such file or directory", 'error'),
  ]
  
  # Render each line
  for i, line_parts in enumerate(shell_lines):
    if start_y + i >= term.height - 2:
      break
    
    y = start_y + i
    x = 2  # Left margin
    
    # Set background color
    bg_r, bg_g, bg_b = hex_to_rgb(color_map['bg'])
    line_content = ""
    
    # Process line parts
    if not line_parts:
      line_content = " " * (width - 4)
    else:
      for j in range(0, len(line_parts), 2):
        if j + 1 < len(line_parts):
          text = line_parts[j]
          color_key = line_parts[j + 1]
          
          if color_key in color_map:
            r, g, b = hex_to_rgb(color_map[color_key])
            # Apply both foreground and background colors
            line_content += term.color_rgb(r, g, b) + term.on_color_rgb(bg_r, bg_g, bg_b) + text
          else:
            # Use normal foreground with background
            nr, ng, nb = hex_to_rgb(color_map['normal'])
            line_content += term.color_rgb(nr, ng, nb) + term.on_color_rgb(bg_r, bg_g, bg_b) + text
        else:
          # Use normal foreground with background for unpaired text
          nr, ng, nb = hex_to_rgb(color_map['normal'])
          line_content += term.color_rgb(nr, ng, nb) + term.on_color_rgb(bg_r, bg_g, bg_b) + line_parts[j]
    
    # Pad line to full width with background color
    padding_len = max(0, width - 4 - len(re.sub(r'\x1b\[[0-9;]*m', '', line_content)))
    if padding_len > 0:
      nr, ng, nb = hex_to_rgb(color_map['normal'])
      line_content += term.color_rgb(nr, ng, nb) + term.on_color_rgb(bg_r, bg_g, bg_b) + " " * padding_len
    
    lines.append((y, x, line_content + term.normal))
  
  return lines

def main():
  term = Terminal()
  themes = get_themes()
  
  if not themes:
    print("No themes found in kitty-themes/themes/")
    return
  
  selected = 0
  scroll_offset = 0
  
  with term.fullscreen(), term.cbreak(), term.hidden_cursor():
    while True:
      print(term.clear)
      
      # Header
      print(term.move_y(1) + term.center(term.bold("Kitty Theme Selector")))
      print(term.move_y(2) + term.center("↑/↓ to navigate, Enter to select, q to quit"))
      
      # Calculate layout
      start_y = 4
      list_height = term.height // 2 - 2
      preview_start_y = start_y + list_height + 2
      preview_height = term.height - preview_start_y - 2
      
      # Update scroll offset to keep selected item visible
      if selected < scroll_offset:
        scroll_offset = selected
      elif selected >= scroll_offset + list_height:
        scroll_offset = selected - list_height + 1
      
      # Theme list
      for i in range(list_height):
        theme_index = scroll_offset + i
        if theme_index >= len(themes):
          break
          
        name, _, colors = themes[theme_index]
        y = start_y + i
        
        if theme_index == selected:
          line = f"> {name}"
          print(term.move_y(y) + term.reverse(line))
        else:
          line = f"  {name}"
          print(term.move_y(y) + line)
      
      # Show scroll indicators
      if scroll_offset > 0:
        print(term.move_y(start_y - 1) + term.center("↑ more themes above ↑"))
      if scroll_offset + list_height < len(themes):
        print(term.move_y(start_y + list_height) + term.center("↓ more themes below ↓"))
      
      # Shell preview for selected theme
      if selected < len(themes):
        _, _, colors = themes[selected]
        
        # Preview header
        print(term.move_y(preview_start_y - 1) + term.center(term.bold("Shell Preview:")))
        
        # Create shell preview
        preview_lines = create_shell_preview(term, colors, preview_start_y, term.width)
        
        # Draw preview border and content
        for y, x, content in preview_lines:
          print(term.move_y(y) + term.move_x(x) + content)
      
      # Handle input
      key = term.inkey()
      
      if key.lower() == 'q':
        break
      elif key.name == 'KEY_UP' and selected > 0:
        selected -= 1
      elif key.name == 'KEY_DOWN' and selected < len(themes) - 1:
        selected += 1
      elif key.name == 'KEY_ENTER':
        theme_name, theme_file, _ = themes[selected]
        if apply_theme(theme_file):
          print(term.move_y(term.height - 1) + term.center(
            term.green(f"Applied theme: {theme_name}! Press any key to exit...")))
          term.inkey()
        else:
          print(term.move_y(term.height - 1) + term.center(
            term.red("Failed to apply theme. Press any key to continue...")))
          term.inkey()
        break

if __name__ == "__main__":
  main() 