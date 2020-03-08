FROM python:latest
ADD . /code
VOLUME /data
WORKDIR /code
RUN pip install -i  https://pypi.doubanio.com/simple/  --trusted-host pypi.doubanio.com -r requirements.txt
CMD ["python", "runc.py"]


