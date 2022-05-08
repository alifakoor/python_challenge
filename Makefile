build:
	pip install -r requirements.txt
run:
	python http_proxy.py

.PHONY: build run