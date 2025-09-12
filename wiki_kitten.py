from typing import List
from kitty.boss import Boss
from kittens.tui.handler import result_handler
from kitty.fast_data_types import get_options
from kitty.utils import color_as_int

def main(args: List[str]):
  pass

def redraw_tab_bar(boss):
  tm = boss.active_tab_manager
  if tm is not None:
    tm.mark_tab_bar_dirty()

def get_wiki_tab_position(tabs):
  i = 1
  for tab in tabs:
    if getattr(tab, "title", None) == 'wiki':
      return i
    i += 1
  return None

def move_wiki_tab_to_end(tabs, boss):
  # assumes that wikiTab is currently focussed
  tabLength = len(tabs)
  wikiTabPosition = get_wiki_tab_position(tabs)
  if wikiTabPosition == tabLength:  # wiki tab is already at the rightmost tab
    return
  if (wikiTabPosition and tabLength > wikiTabPosition):
    current_position = wikiTabPosition
    while (current_position < tabLength):
      boss.move_tab_forward()  # this moves the currently focussed tab
      current_position += 1

@result_handler(no_ui=True)
def handle_result(args: List[str], answer: str, target_window_id: int, boss: Boss) -> None:
  # go to tab named 'wiki'
  # if tab does not exist, create the tab
  # if currently focussed tab is the 'wiki' tab, then go to previous tab
  # change the 'wiki' tab colour
  
  tm = boss.active_tab_manager
  opts = get_options()
  
  # Use theme colors instead of hardcoded ones
  accent_color = color_as_int(opts.color3)  # Usually orange/yellow in most themes
  text_color = color_as_int(opts.active_tab_foreground)
  
  is_wiki_focussed = False
  if boss.active_tab.title == 'wiki':
    is_wiki_focussed = True
  
  tabs = boss.match_tabs('title:^wiki')
  tab = next(tabs, None)  # default value for generator to None instead of throwing StopIteration error
  
  if tab:
    # Set wiki tab colors using theme colors
    tab.inactive_fg = accent_color
    tab.active_fg = text_color
    tab.active_bg = accent_color
    redraw_tab_bar(boss)
    
    if not is_wiki_focussed:
      boss.set_active_tab(tab)
    else:
      # assumes that tab is wiki tab and is currently focussed
      move_wiki_tab_to_end(tm.tabs, boss)
      # go to previous active tab
      boss.goto_tab(0)  # go to previous active tab
  else:
    boss.launch(
      "--type=tab",
      "--title=wiki",
      "--cwd=/Users/matter/vimwiki",
    ) 