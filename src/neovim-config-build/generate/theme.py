#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃                                        Will be used:                                         ┃
#    ┃    1. Template from Lua code which will be filled with variables (repo, colorscheme name)    ┃
#    ┃                                2. brain (But not guarranting)                                ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


#  ─────────────────────────── Imports (Will be used in future generation) ────────────────────────────
from generate.logger import configure_logger

# Start only from ../ and with "python -m generate.theme"

"""
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃    EXAMPLE OF TEMPLATE:    ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
return {
    repo,
    priority = 1000,
    lazy = false
    vim.cmd("colorscheme " .. name)
    end,
}
"""

file_to_save: str = "theme"
logger = configure_logger(file_to_save)
theme_name, colorscheme = tuple(
    input("Write the theme name and colorscheme - separate with |: ")
    .strip()
    .split("|", 1)
)
logger.info(f"User's theme: {theme_name} | User's colorscheme {colorscheme}")
print(f"Theme name is: {theme_name}, and a colorscheme is {colorscheme}!")
