FROM tiangolo/uwsgi-nginx:python3.8

ENV APP_VERSION 0.1.21
################## CONFIG VARIABLES ##################
ENV LISTEN_PORT 5000

ENV FLASK_BIND_PORT 5000
ENV FLASK_BIND_HOST 0.0.0.0

ENV FLASK_CONFIG_SECRET_KEY asdf3892wegqhodssa
################## END CONFIG VARIABLES ##################

RUN apt-get update \
    && apt-get install -y \
        ca-certificates gcc libffi-dev libssl-dev bash curl wget

# Copy api code in place
COPY ./eco_aprs_weather /app/eco_aprs_weather/
COPY ./MANIFEST.in /app
COPY ./requirements.txt /app
COPY ./setup.cfg /app
COPY ./setup.py /app

# Install flask api
RUN python3 /app/setup.py install

# Uwsgi customization
COPY ./app/uwsgi.ini /etc/uwsgi/uwsgi.ini

# Nginx customization
COPY config/nginx/nginx.conf /etc/nginx/nginx.conf
COPY config/nginx/upload.conf /etc/nginx/conf.d/upload.conf
COPY config/nginx/uwsgi.conf /etc/nginx/conf.d/uwsgi.conf

# HotFix ownership so we can run nginx/supervisord/flask as non-root container
RUN chown -R nginx:nginx /var/cache/nginx \
    && chown -R nginx:nginx /var/log/nginx \
    && chown -R nginx:nginx /etc/nginx \
    && touch /var/run/nginx.pid \
    && chown -R nginx:nginx /var/run/nginx.pid \
    && chown -R nginx:nginx /var/log/supervisor \
    && chown -R nginx:nginx /etc/supervisor \
    && chown -R nginx:nginx /run/

# Copy supervisord config with non-root capability
COPY config/supervisord/conf.d/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run everything as non-root!
USER nginx