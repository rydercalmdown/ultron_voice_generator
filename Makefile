IMAGE_NAME=ryderdamen/voice_cloning_server
VERSION=0.0.1
HOST=0.0.0.0

.PHONY: install
install:
	@export IMAGE_NAME=$(IMAGE_NAME):$(VERSION) && cd deployment && bash install.sh

.PHONY: build
build:
	@make install

.PHONY: run
run:
	@docker run -v $(shell pwd)/tmp:/tmp -p 8000:8000 $(IMAGE_NAME):$(VERSION) python app.py

.PHONY: test
test:
	@curl -X POST $(HOST):8000/generate/ -F 'file=@test/test_1.wav' -F 'text="Hello how are you doing?"' --output result.wav

.PHONY: push
push:
	@docker push $(IMAGE_NAME):$(VERSION)
