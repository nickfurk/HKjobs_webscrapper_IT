FROM python:3.9

ADD webcrawler.py .
ADD jobsSchema.sql .

RUN pip install requests mysql-connector-python beautifulsoup4

ENV MYSQL_HOST="host.docker.internal"
ENV USER="root"
ENV PASSWORD="chefsunion1234"

CMD ["python", "webcrawler.py"]