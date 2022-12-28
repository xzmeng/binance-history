coverage:
	pytest --cov && coverage html && open -a "Google Chrome" htmlcov/index.html

clean:
	rm .coverage && rm -rf htmlcov/ && rm -rf dist/ && rm -rf .pytest_cache/ && rm -rf tests/.pytest_cache