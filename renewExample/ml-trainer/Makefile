
all:
	build run

build:
	docker build -t skyface753/ml-trainer:latest .

run:
	docker run -it --rm -v $(PWD)/MLModels:/trainer/MLModels skyface753/ml-trainer:latest
