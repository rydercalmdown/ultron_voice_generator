IMAGE_NAME=ryderdamen/voice_cloning_server

.PHONY: install
install:
	@export IMAGE_NAME=$(IMAGE_NAME) && cd deployment && bash install.sh

.PHONY: build
build:
	@make install

.PHONY: run
run:
	@docker run -v $(shell pwd)/tmp:/tmp -p 8000:8000 $(IMAGE_NAME) python app.py

.PHONY: test
test:
	@curl -X POST 0.0.0.0:8000/generate/ -F 'file=@test/test_1.wav' -F 'text="hello how are you"' --output result.wav

.PHONY: push
push:
	@docker push $(IMAGE_NAME)
