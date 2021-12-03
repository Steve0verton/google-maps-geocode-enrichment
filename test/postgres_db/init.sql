CREATE TABLE ref_location
(
    location_hash text,
    location text,
    enrichment_enabled boolean,
    enrichment_status text,
    formatted_address text,
    latitude numeric(11,6),
    longitude numeric(11,6),
    load_dttm timestamp,
    last_update_dttm timestamp,
    google_place_id text,
    google_partial_match boolean,
    google_result_count integer,
    google_result_type jsonb,
    long_street_number text,
    long_route text,
    long_political text,
    long_locality text,
    long_postal_code text,
    long_postal_code_suffix text,
    long_postal_town text,
    long_premise text,
    long_country text,
    long_admin_area_level_1 text,
    long_admin_area_level_2 text,
    long_admin_area_level_3 text,
    long_admin_area_level_4 text,
    long_admin_area_level_5 text,
    long_establishment text,
    short_street_number text,
    short_route text,
    short_political text,
    short_locality text,
    short_postal_code text,
    short_postal_code_suffix text,
    short_postal_town text,
    short_premise text,
    short_country text,
    short_admin_area_level_1 text,
    short_admin_area_level_2 text,
    short_admin_area_level_3 text,
    short_admin_area_level_4 text,
    short_admin_area_level_5 text,
    short_establishment text,
    location_type jsonb,
    enrichment_api_response jsonb,
    CONSTRAINT pk_location_hash PRIMARY KEY (location_hash)
);

COMMENT ON TABLE ref_location
    IS 'Fixed dimension with records treated as a cache of location queries to lookup from external geocode API.';

CREATE INDEX idx_enrichment_enabled
    ON ref_location USING btree
    (enrichment_enabled);

CREATE INDEX idx_enrichment_status
    ON ref_location USING btree
    (enrichment_status);

CREATE INDEX idx_location
    ON ref_location USING btree
    (location);

CREATE INDEX idx_location_hash
    ON ref_location USING hash
    (location_hash);
