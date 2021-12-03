FROM postgres:latest

WORKDIR /tmp

# Copy initialization SQL files and shell scripts into docker entrypoint which are automatically executed on startup
COPY *.sql /docker-entrypoint-initdb.d/
COPY *.sh /docker-entrypoint-initdb.d/
COPY *.csv /tmp/
