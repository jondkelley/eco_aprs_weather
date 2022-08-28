apt-get install -7 ruby ruby-dev rubygems build-essential
gem install --no-document fpm

fpm  --python-bin python3 --python-pip pip3 --python-package-name-prefix python3 -s python -t deb eco-aprs-weather
fpm  --python-bin python3 --python-pip pip3 --python-package-name-prefix python3 -s python -t snap eco-aprs-weather
fpm  --python-bin python3 --python-pip pip3 --python-package-name-prefix python3 -s python -t rpm eco-aprs-weather
fpm  --python-bin python3 --python-pip pip3 --python-package-name-prefix python3 -s tar -t rpm eco-aprs-weather
fpm  --python-bin python3 --python-pip pip3 --python-package-name-prefix python3 -s zip -t rpm eco-aprs-weather

