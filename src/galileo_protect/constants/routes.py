from types import SimpleNamespace

# We cannot use Enum here because `mypy` doesn't like it when we format those routes
# into strings. https://github.com/python/mypy/issues/15269
Routes = SimpleNamespace(
    invoke="protect/invoke", stages="projects/{project_id}/stages", stage="projects/{project_id}/stages/{stage_id}"
)
