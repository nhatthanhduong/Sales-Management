FROM python:3.11.8

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

RUN pybabel compile -d translations

ENTRYPOINT [ "python" ]
CMD ["product_sales.py"]