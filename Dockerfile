FROM python:3.9.12-buster
ADD . /
WORKDIR /
RUN make
CMD ["make", "run"]