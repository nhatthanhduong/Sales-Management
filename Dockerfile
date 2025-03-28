FROM python:3.11.8

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# ENV FLASK_APP=product_sales.py
# ENV FLASK_RUN_HOST=0.0.0.0
# ENV FLASK_ENV=development

ENTRYPOINT [ "python" ]
CMD ["product_sales.py"]