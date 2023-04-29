FROM python:3.10 AS MLtrainer
ENV PYTHONUNBUFFERED 1
RUN mkdir /trainer
WORKDIR /trainer
ADD requirements.txt /trainer/
RUN pip install -r requirements.txt
ADD *.py /trainer/
ADD solar-power-generation-data/*.csv /trainer/solar-power-generation-data/
RUN mkdir /trainer/MLModels
CMD ["python", "model_trainer.py"]
# RUN python model_trainer.py

