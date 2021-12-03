FROM geocode_lib
WORKDIR /app
ADD . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "app.py"]
