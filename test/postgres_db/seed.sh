#!/bin/bash
set -e

psql -c "COPY ref_location FROM '/tmp/ref_location_sample.csv' CSV HEADER"
