.PHONY: start setup deploy

start:
	poetry run main

setup:
	poetry install

deploy:
	git push origin main
	git update-ref -d refs/heads/production
	git checkout -b production
	git push origin production -f
	git checkout main
