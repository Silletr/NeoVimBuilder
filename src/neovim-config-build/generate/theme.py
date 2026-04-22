#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃                                        Will be used:                                         ┃
#    ┃    1. Template from Lua code which will be filled with variables (repo, colorscheme name)    ┃
#    ┃                                2. brain (But not guarranting)                                ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


#  ─────────────────────────── Imports (Will be used in future generation) ────────────────────────────
from difflib import SequenceMatcher
import sys

import requests

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

    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃    Repository search example    ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    https://api.github.com/search/repositories?q={query}

"""

#  ────────────────────────────────────────────────────────────────────────────────────────────────────
file_to_save: str = "theme"
logger = configure_logger(file_to_save)
theme_name, colorscheme = tuple(
    input("Write the theme name and colorscheme - separate with |: ")
    .strip()
    .split("|", 1)
)

if not theme_name or not colorscheme:
    logger.error("Use the format! \nTheme | Colorscheme")

logger.info(f"User's theme: {theme_name} | User's colorscheme {colorscheme}")
print(f"Theme name is: {theme_name}, and a colorscheme is {colorscheme}!")


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃    Find a repo with limited value    ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
def format_repo_list(items, limit=3):
    lines = []
    for i, r in enumerate(items[:limit], start=1):
        lines.append(f"{i}. {r['full_name']}")
    return "\n".join(lines)


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃    find a match between user input and app result    ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
def similarity(origin: str, to_match: str) -> float:
    return SequenceMatcher(None, origin.lower(), to_match.lower()).ratio()


#  ────────────────────────────────────────────────────────────────────────────────────────────────────
# Search for Repo by User's theme name
req = requests.get(f"https://api.github.com/search/repositories?q={theme_name}")
if req.status_code != 200:
    logger.error(f"Requests.get() got an error! Status code: {req.status_code}")

data = req.json()
items_to_check = data.get("items", [])
logger.success(
    f"""
    Got a theme on Github! Found \n{len(items_to_check)} repo's,
    The {items_to_check[0]["full_name"]} is the correct one!
    """
)

if not items_to_check:
    logger.error(f"No repositories found by: {theme_name}")
    sys.exit(1)

repo = items_to_check[0]["full_name"]  # e.g EdenEast/nightfox.nvim
logger.success(f"Found repo: {repo}")
# especially for me, to remember indexes xD:
# repo 1   repo 2   repo 3
# 0        1         2


score = similarity(theme_name, repo)

if theme_name.lower() in repo.lower() or score > 0.8:
    selected_repo = repo
    logger.success(f"Auto-selected: {repo} (score={score:.2f})")
    print(f"Auto-selected: {repo}")
else:
    logger.info(f"low match ({score:.2f}), asking user")
    print(f"low match ({score:.2f}), select pls!")

    repo_list = format_repo_list(items=items_to_check, limit=10)

    user_choose = int(
        input(
            f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        Repository:         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
{repo_list}

>>> """
        )
    )

    selected_repo = items_to_check[user_choose - 1]["full_name"]
    logger.success(f"Found repo: {selected_repo}")
    print(f"Got you, then I'll remember - {user_choose} is the correct one!")
