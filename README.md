# Google Maps Geocode Enrichment

This project repository provides a headless module to enrich location data in a database table using the Google Maps Geocode API.

## Table of Contents

## Background

This module was built to provide data cleansing and enrichment for physical mailing address locations scraped from public data sources.  Street address locations can contain many typos, variations in spellings, misspellings and other problems.  The [Google Maps Geocode Service](https://developers.google.com/maps/documentation/geocoding/overview) was selected as a source of data enhancement and enrichment because Google Maps is one of the best sources of location-based addresses across the world and because of the advanced Natural Language Prediction (NLP) capabilities inherent in using this service for address resolution.

The original design of this data enrichment module leveraged the following outputs from the Geocoding API:
1. Latitude / Longitude coorindates for a street address
2. Standardized cleansed street address
3. Tokenized pieces of the street address for additional filtering, analysis and grouping (i.e. parse "NC" from and address in North Carolina and store in a "State" column)

The scope of this module is intended to be a headless engine running on an as-needed basis to update records in a database table as a part of a broader data management pipeline.  Example use cases include data warehousing and data lakes.

## Technical Overview

This project repository provides source code to build a process to enrich address locations via the [Google Geocode API](https://developers.google.com/maps/documentation/geocoding/overview).  The source code is in python and is containerized with Docker.  This serves to address 2 main concerns.  First that it is written in a language that is approachable for data analysis purposes, and second it's efficient and fast enough to provide **~500,000 updates in 1 day**.  Parallelization of the Google API interaction step is needed to meet the latter criteria, and containerization serves as a useful means to accomplish that.


## Google Web Services Legal Disclaimer

Google provides explicit terms of use for their products.  This application leverages the **Geocoding API** service which has policies to be considered for your intended use of the data retrieved. Sections related to **pre-fetching** and **caching** of content apply directly to this application. Google explicitly states that data from the Geocoding API must not be pre-fetched, cached, or stored except under limited conditions.  

- [Geocoding API Policies](https://developers.google.com/maps/documentation/geocoding/policies)
- [Google Maps Platform Terms of Service](https://cloud.google.com/maps-platform/terms)
- [Google Maps Platform Service Specific Terms](https://cloud.google.com/maps-platform/terms/maps-service-terms)

The author of this project repository and application makes no legal recommendations or interpretations on how to adhere to Google Geocoding API policies for applications developed commercially or contained within your on-premise environment. Use at your own discretion.


## Project Directory Structure

Key components are organized into the following directory structure:
- [/cluster](./cluster) - Production code is contained in **cluster**.  It reuses the library code used by the experimental code, but is organized as standalone apps (assumed running each within a docker) that communicate via **Kafka**. Contains docker files, python app.py files, docker compose yml files - the main code and components for establishing and running the kafka infrasturcutre and apps to establish many clients to ping the Google Maps API using the bulk key and return results to the PostgreSQL database.
  - [../infra](./cluster/infra) - **docker-compose.yml** specifies serivces for kafka queueing (zookeeper and kafka services) and includes environment variables and connection properties for services (ports, kafka topics, docker network, etc).
  - [../app](./cluster/app)
    - **docker-compose.yml**
    - [.../g_query](./cluster/app/g_query) - Contains docker file and app.py file that contains the Google Maps API Key and functions to look up each location and bring back results.
    - [.../pg_query](./cluster/app/pg_query) - Contains docker file and app.py file that contains the DB credentials to connect to the DB using a SQL statement specifying to pull records with a null enrichment status or records that have not been looked up within the past 30 days.
    - [.../pg_update](./cluster/app/pg_update) - Contains docker file and app.py file that is responsible for updating the DB with the additional enhanced address information.
- [/doc](./doc) - Project documentation. Example DDL provided for creating the ref_location database table used to cache geocode results by location.
- [/lib](./lib) - Library code is contained in **lib**.  It constitutes the core reusable components for obtaining work from postgres, querying and collecting results from Google, and updating postgres.  Both the experimental code as well the the production cluster code makes use of it in the same way.
- [/test](./test) - Experiments, testing and debugging code.  Different aspects of the dev process are illustrated here and can serve as simplistic checks for additional features.


## Prerequisites

Use of this application requires working knowledge of the following technologies:

- [Docker](https://www.docker.com/)
- [Python](https://www.python.org/)
- [Google Cloud Platform](https://cloud.google.com/)
- [Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding/overview)

### Technical Prerequisites

- Command Line Interface
  - Mac and Linux machines natively support
  - Windows machines will need a [linux subsystem](https://docs.microsoft.com/en-us/windows/wsl/install)

#### Google Maps Geocode API Credentials

This application requires an API key to query the [Google Maps Geocode API](https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com).  You must have the Geocoding API enabled from within the Google Cloud console as well as a functioning API key.

- [Geocoding API](https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com)


#### Docker Requirements

This application requires the latest version of Docker installed and running.

- [Get Docker](https://docs.docker.com/get-docker/)

This application leverages a Docker network to containerize network activity. **docker-compose.yml** files within [/cluster](./cluster) reference the **geocode** network.

```bash
docker network create geocode
```


#### Python Requirements

This application requires the latest version of Python installed.

- [Download Python](https://www.python.org/downloads/)


## Technical Component Overview

The following list provides an overview of key components:
- PostgreSQL database
- geocode_lib library (custom python application written in Docker)
- Kafka infrastructure
- Enrichment process (custom python applications built with docker compose)

### Dependencies

PostgreSQL and Kafka must be running before the enrichment process begins.  The `geocode_lib` Docker image must be built as well.  The enrichment process leverages these in a service-oriented manner.

### Parallelized Enrichment Process

Queries to Google must be parallelized; to accomplish this, a single client (**pg_query**) interacts with postgres, places the query on a kafka topic **geocode_input**, multiple clients (**g_query**) take these queries in parallel and convert the result to a format usable by the to-progres process and place it in a result topic **geocode_output**. And finally a single process (**pg_update**) reads the contents of that output topic and updates the database with the results.

The rate limiting is controlled by **pg_query**.


### Kafka Partitions

To allow the parallelism concept to work, the geocode_input Kafka topic must have a number of partitions greater or equal to the number of g_query clients.

Enter the running Kafka Docker container.
```bash
docker exec -it infra_kafka_1 /bin/bash
```

Set partitions on a new topic
```bash
kafka-topics.sh --create --zookeeper zookeeper --topic geocode_input --partitions 50 --replication-factor 1
```

Or if the topic already exists
```bash
kafka-topics.sh --alter --zookeeper zookeeper --topic geocode_input --partitions 50
```


## Deployment Instructions

The following steps can be used to build a local environment for development and testing purposes or a production environment for data enrichment as a part of an ETL data flow process.

1. **Define Docker Network**

  ```bash
  docker network create geocode
  ```

  If the network already exists, Docker will display a message.

2. **Build and Start PostgreSQL Database Container (if desired) for development and testing purposes only.** Production data management flows will most likely have other PostgreSQL database sources which can be configured within the [docker-compose.yml](./cluster/app/docker-compose.yml) file.  Further instructions provide steps to configure this file.

  Switch to Docker image definition from the project root.
  ```bash
  cd test/postgres_db
  ```

  Build PostgreSQL Docker image using the Dockerfile.
  ```bash
  docker build -t postgres .
  ```
  - The [Dockerfile](./test/postgres_db/Dockerfile) defines steps used to deploy the latest version of PostgreSQL for development and testing purposes.
  - The **init.sql** file is copied into the Docker image and executed when the container is started, which creates the required **ref_location** database table used to cache location enrichment data.
  - The **seed.sh** script is copied into the Docker image and executed when the container is started, which seeds sample data from the [ref_location_sample.csv](./test/postgres_db/ref_location_sample.csv) file.
  - Sample location data is copied into the Docker image and deployed when the container starts using CSV files within [/test/postgres_db](./test/postgres_db). The [ref_location_sample.csv](./test/postgres_db/ref_location_sample.csv) file is used by default.

  Start the PostgreSQL Container from the image named `postgres` created previously. The `--network` parameter `geocode` references the Docker network created previously. The `-p` parameter maps the default PostgreSQL port of `5432` from the Docker network to your local network. Create your own password using the `POSTGRES_PASSWORD` parameter.
  ```bash
  docker run --name postgres --network geocode -p 5432:5432/tcp -e POSTGRES_PASSWORD=YOUR_PASSWORD -d postgres
  ```

  Connect to the PostgreSQL database using a tool such as [pgAdmin](https://www.pgadmin.org/) to test the database connectivity and explore the sample data contained within the **ref_location** table.  The sample database created in this process is the latest version of PostgreSQL with a database called `postgres`, a user named `postgres` and a password set when running the Docker container.

3. **Build Geocode Library Docker Image**

  Switch to Docker image definition from the project root.
  ```bash
  cd lib
  ```

  Build `geocode_lib` Docker image using the Dockerfile.
  ```bash
  docker build -t geocode_lib .
  ```
  - The [Dockerfile](./lib/geocode_lib/Dockerfile) defines how the Python application is built.

  The `geocode_lib` Docker image is built using [python code](./lib/geocode_lib) to help translate data between the Geocode API and the PostgreSQL target database.

4. **Build and Deploy Kafka Infrastructure**

  Switch to Docker image definition from the project root.
  ```bash
  cd cluster/infra
  ```

  Build and start the Kafka infrastructure using docker-compose.
  ```bash
  docker-compose up -d
  ```
  - The [docker-compose.yml](./cluster/infra/docker-compose.yml) defines how Kafka is deployed.
  - Official images are built from the [wurstmeister](https://hub.docker.com/r/wurstmeister/kafka) Docker hub.

  The `docker-compose` command above builds and runs the Docker container in the background.

5. **Build Apps** for retrieving locations to enrich, querying the geoode API and updating location data in target database.

  Switch to Docker image definition from the project root.
  ```bash
  cd cluster/app
  ```

  Build and start the application using docker-compose.
  ```bash
  docker-compose up -d --scale g_query=5
  ```
  - The [docker-compose.yml](./cluster/app/docker-compose.yml) defines the application engine as well as critical credentials for the Google Geocode API and target PostgreSQL database. Update the `API_KEY`, `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` accordingly. By default, the `POSTGRES_HOST` variable points to the sample PostgreSQL database image within the Docker network created previously

  The `docker-compose` command above builds and runs the Docker container in the background.

## Common Test Examples

### Interactive Geocode API JSON Response from Web Browser

To simulate the Geocode API interactively from a web browser and visually understand the JSON response, use the following URL structure with your API key:

``https://maps.googleapis.com/maps/api/geocode/json?address=1030%20Richardson%20Dr,%20Raleigh,%20NC%2027603&key=ENTER_YOUR_API_KEY``


## Standards

### File Properties

 - filenames must be lowercase using underscores
 - unix style line endings (LF)
 - UTF-8 encoding

### Coding Standards

 - Indentation = 2 spaces with no tabs.
 - Empty lines separating major steps.
 - The phrase **NOTE:** is used to highlight important notes throughout code.
 - The phrase **TODO:** is used to note future enhancements.
 - Environment variables are named with all capital letters and underscores
 - Python variables are named in camel case


## Author Contact

 - [Steve Overton](https://www.linkedin.com/in/overton/)
