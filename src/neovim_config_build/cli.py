from neovim_config_build.generate.theme import get_theme_config
import typer


app = typer.Typer()


@app.command()
def generate_theme(
    theme_name: str,
    colorscheme: str,
):
    config = get_theme_config(theme_name, colorscheme)
    typer.echo(config)


if __name__ == "__main__":
    app()
