FROM python:latest
RUN yum install -y python-devel  gcc gcc-c++ autoconf automake libtool make
ENV PATH /usr/local/bin:$PATH
ADD . /code
VOLUME /data
WORKDIR /code
RUN pip install -i  https://pypi.doubanio.com/simple/  --trusted-host pypi.doubanio.com -r requirements.txt
CMD ["python", "run.py"]


