############################################################
# Dockerfile to build a Website
# Based on Ubuntu
# Installs Python3.6, Flask, Apache2, ODBC and Kerberos
############################################################

# Set the base image
FROM ubuntu:16.04

# File Author / Maintainer
MAINTAINER Matt Camp

# apt-get and system utilities
RUN apt-get update \
    && apt-get install -y \
    curl apt-utils apt-transport-https debconf-utils gcc build-essential g++-5\
    && DEBIAN_FRONTEND=noninteractive \
    apt-get -y install libc6 \
    libpam-krb5 \
    krb5-user  \
    libgssapi-krb5-2 \
    libstdc++6 \
    libkrb5-3 \
    libcurl3 \
    openssl \
    debconf \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

###############################################################
# Instal M$ ODBC Drivers for SQL Server (Optional)
# NOTE: Comment out this section for ARM boards..
###############################################################

# adding custom MS repository
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# install SQL Server drivers
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql unixodbc-dev

# install SQL Server tools
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN /bin/bash -c "source ~/.bashrc"

# install necessary locales
RUN apt-get -qq update && apt-get -qqy install locales \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen

###############################################################
# Copy over Kerberos config files (Optional)
###############################################################
# COPY ./krb5.conf /etc/krb5.conf
# COPY ./common-session /etc/pam.d/common-session


###############################################################
# Setup Apache & mod_wsgi for Python 3.6
###############################################################
RUN apt-get update \
    && apt-get -y install \
    apache2 \
    apache2-dev \
    curl

# Uncomment for ARM based boards... and comment out the next line
#COPY ./apache-flask-arm.conf /etc/apache2/sites-available/apache-flask.conf
COPY ./apache-flask.conf /etc/apache2/sites-available/apache-flask.conf
RUN a2ensite apache-flask
RUN a2enmod headers

RUN apt-get update \
    && apt-get -y install software-properties-common python-software-properties
RUN add-apt-repository ppa:jonathonf/python-3.6 \
    && apt-get update \
    && apt-get -y install python3.6 \
    python3.6-dev \
    python3.6-venv

WORKDIR /usr/local/src

RUN curl -O https://bootstrap.pypa.io/get-pip.py \
    && python3.6 get-pip.py \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1 \
    && pip install mod_wsgi

RUN mod_wsgi-express install-module

COPY ./requirements.txt /var/www/apache-flask/requirements.txt
RUN pip install -r /var/www/apache-flask/requirements.txt

RUN a2ensite apache-flask
RUN a2enmod headers

COPY ./ /var/www/apache-flask/

RUN a2dissite 000-default.conf
RUN a2ensite apache-flask.conf

EXPOSE 80

WORKDIR /var/www/apache-flask

CMD  /usr/sbin/apache2ctl -D FOREGROUND