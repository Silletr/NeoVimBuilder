#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃                                        Will be used:                                         ┃
#    ┃    1. Template from Lua code which will be filled with variables (repo, colorscheme name)    ┃
#    ┃                                2. brain (But not guarranting)                                ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


#  ─────────────────────────── Imports (Will be used in future generation) ────────────────────────────
from difflib import SequenceMatcher
import sys
from pathlib import Path

import requests

from neovim_config_build.generate.logger import configure_logger

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

file_to_save: str = "theme"
logger = configure_logger(file_to_save)


#  ────────────────────────────────────────────────────────────────────────────────────────────────────
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
def fetch_github_repos(theme_name):
    url = f"https://api.github.com/search/repositories?q={theme_name}"
    try:
        req = requests.get(url)
        logger.success(f"Fetched repositories for: {theme_name}")
        if req.status_code != 200:
            logger.error(f"GitHub API request failed! Status code: {req.status_code}")
            sys.exit(1)

        data = req.json()
        items = data.get("items", [])
        logger.success(f"Found {len(items)} repository(ies) for: {theme_name}")
        if not items:
            logger.error(f"No repositories found for: {theme_name}")
            sys.exit(1)

        return items
    except Exception as e:
        logger.error(f"Error fetching GitHub repositories: {e}")
        sys.exit(1)


#  ────────────────────────────────────────────────────────────────────────────────────────────────────


def pick_best_repo(theme_name, items):
    repo = items[0]["full_name"]
    score = similarity(theme_name, repo)

    logger.success(f"Best candidate: {repo} (score={score:.2f})")

    if theme_name.lower() in repo.lower() or score > 0.8:
        selected_repo = repo
        logger.success(f"Auto-selected: {selected_repo} (score={score:.2f})")
        print(f"Auto-selected: {selected_repo}")
        return selected_repo, theme_name  # repo, colorscheme

    logger.info(f"Low match ({score:.2f}), asking user to choose")
    print(f"Low match ({score:.2f}), please select:")

    repo_list = format_repo_list(items=items, limit=10)

    try:
        choice = int(
            input(
                f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        Repository:         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
{repo_list}

>>> """
            )
        )
    except (ValueError, IndexError):
        logger.error("Invalid input. Please enter a valid number.")
        sys.exit(1)

    selected_repo = items[choice - 1]["full_name"]
    logger.success(f"User selected: {selected_repo}")
    print(f"Got you, {choice} is the correct one!")
    return selected_repo, theme_name  # repo, colorscheme


def get_github_theme_repo(theme_name):
    items = fetch_github_repos(theme_name)
    return pick_best_repo(theme_name, items)


def apply_theme(full_theme_name: str, colorscheme_name: str) -> str:
    template = f"""return {{
    {{
        '{full_theme_name}',
        priority = 1000,
        lazy = false,
        config = function()
            vim.cmd("colorscheme {colorscheme_name}")
        end
    }}
}}"""
    return template


#  ────────────────────────────────────────────────────────────────────────────────────────────────────
def get_theme_config(theme_name: str, colorscheme: str):
    """Full pipeline: search repo → pick best → generate config"""
    repo, _ = get_github_theme_repo(theme_name)
    return apply_theme(repo, colorscheme)


def save_to_config(theme_name: str, theme_code: str):
    """Create ~/.config/nvim/lua/plugins/{theme_name}.lua"""
    config_dir = Path.home() / ".config" / "nvim" / "lua" / "plugins"
    config_dir.mkdir(parents=True, exist_ok=True)

    file_path = config_dir / f"{theme_name}.lua"
    file_path.write_text(theme_code, encoding="utf-8")


if __name__ == "__main__":
    file_to_save: str = "theme"
    logger = configure_logger(file_to_save)

    raw = input("Write the theme name and colorscheme - separate with |: ").strip()
    parts = [part.strip() for part in raw.split("|", 1)]

    if len(parts) != 2 or not parts[0] or not parts[1]:
        logger.error("Use the format: Theme | Colorscheme")
        raise SystemExit(1)

    theme_name, colorscheme = parts
    logger.info(f"User's theme: {theme_name} | User's colorscheme: {colorscheme}")

    theme_code = get_theme_config(theme_name, colorscheme)
    print(theme_code)

    save_to_config(theme_name, theme_code)
