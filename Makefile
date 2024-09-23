.PHONY: start setup deploy

start:
	clear
	@poetry run main

setup:
	clear
	@poetry install

deploy:
	git push origin main
	git update-ref -d refs/heads/production
	git checkout -b production
	git push origin production -f
	git checkout main
