.PHONY: pep, install, test, clean

pep:
	pep8 ./ --ignore=E501,E701

install:
	pip install -r requirements.txt

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

run:
	python run.py
