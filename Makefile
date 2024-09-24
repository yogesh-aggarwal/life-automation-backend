.PHONY: start setup deploy

PRODUCTION_BRANCH=production

start:
	clear
	@poetry run main

dev: start

clean:
	@rm -rf ./**/__pycache__/

setup:
	clear
	@poetry install

deploy:
	@git push origin main
	@git update-ref -d refs/heads/$(PRODUCTION_BRANCH)
	@git checkout -b $(PRODUCTION_BRANCH)
	@git push origin $(PRODUCTION_BRANCH) -f
	@git checkout main
