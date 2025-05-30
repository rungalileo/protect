from platform import system

from invoke.context import Context
from invoke.tasks import task

# Disable `pty` on Windows to avoid issues with subprocesses.
# https://github.com/pyinvoke/invoke/issues/561
COMMON_PARAMS = dict(echo=True, pty=not system().lower().startswith("win"))


@task
def install(ctx: Context) -> None:
    ctx.run("poetry install --all-extras --without docs --no-root", **COMMON_PARAMS)


@task
def setup(ctx: Context) -> None:
    install(ctx)
    ctx.run("poetry run pre-commit install --hook-type pre-push", **COMMON_PARAMS)


@task
def test(ctx: Context) -> None:
    ctx.run("poetry run pytest -vvv --cov=galileo_core --cov-report=xml", **COMMON_PARAMS)


@task
def type_check(ctx: Context) -> None:
    ctx.run("poetry run mypy --package galileo_protect --namespace-packages", **COMMON_PARAMS)
    ctx.run("poetry run mypy --package tests --namespace-packages", **COMMON_PARAMS)


@task
def docs_build(ctx: Context) -> None:
    ctx.run("poetry run mkdocs build", echo=True)
