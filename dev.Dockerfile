FROM python:3 as build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

RUN ["apt-get", "update"]
RUN ["apt-get", "install", "binutils", "libproj-dev", "gdal-bin", "-y"]

COPY requirements.txt /code/
RUN ["pip", "install", "-r", "requirements.txt"]

COPY . /code/

FROM build as migrate

COPY ./docker-entrypoint.dev.sh /code/

RUN ["chmod", "+x", "/code/docker-entrypoint.sh"]
RUN ["chmod", "+x", "/code/bin/wait-for-it.sh"]

ENTRYPOINT ["bash", "/code/docker-entrypoint.sh"]
