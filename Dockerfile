FROM python:3.6

# Set correct timezone and clean up to decrease image size.
# 'apt-get remove' will also remove /etc/localtime so we have to make a copy first.
RUN apt-get update && \
    apt-get install -y tzdata && \
	cp /usr/share/zoneinfo/Europe/Amsterdam /tmp/localtime && \
	apt-get remove -y tzdata && \
	apt-get autoremove -y && \
	rm -rf /var/cache/apt/* && \
	mv /tmp/localtime /etc/localtime

# Install everything required to run the CherryPy application.
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

# server.py contains the code for the application, site.conf contains the configuration of cherrypy.
COPY server.py site.conf /usr/src/app/
WORKDIR /usr/src/app

# Normally CherryPy uses port 80, but in site.conf we change that to 80.
EXPOSE 80

ENTRYPOINT ["cherryd", "-i", "server", "-c", "site.conf"]
