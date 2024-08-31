from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page


def on_pre_build(config: MkDocsConfig) -> None:
    pass


def on_page_markdown(markdown: str, page: Page, config: MkDocsConfig, files: Files) -> None:
    pass
