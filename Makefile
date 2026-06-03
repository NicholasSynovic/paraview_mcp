.PHONY: build create-dev

build:
	rm -rf dist
	git tag | tr -s '[:blank:]' '\n' | sort | tail -n 1  | xargs -I % uv version %
	uv build
	uv pip install dist/*.tar.gz

create-dev:
	conda env update --file environment.yaml --prune
	conda run -n paraview_mcp pre-commit install
	rm -rf .venv
	conda run -n paraview_mcp uv sync
