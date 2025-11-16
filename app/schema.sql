-- Database Schema --

-- clean slate 

DROP TABLE IF EXISTS election_result CASCADE;
DROP TABLE IF EXISTS candidacy CASCADE;
DROP TABLE IF EXISTS voting_station CASCADE;
DROP TABLE IF EXISTS candidate CASCADE;
DROP TABLE IF EXISTS race CASCADE;
DROP TABLE IF EXISTS election CASCADE;
DROP TABLE IF EXISTS ward_population CASCADE;
DROP TABLE IF EXISTS ward_income CASCADE;
DROP TABLE IF EXISTS ward_education CASCADE;
DROP TABLE IF EXISTS ward_age_gender CASCADE;
DROP TABLE IF EXISTS ward_labour_force CASCADE;
DROP TABLE IF EXISTS ward_transport_mode CASCADE;
DROP TABLE IF EXISTS ward_crime CASCADE;
DROP TABLE IF EXISTS ward_disorder CASCADE;
DROP TABLE IF EXISTS ward_transit_stops CASCADE;
DROP TABLE IF EXISTS ward_recreation CASCADE;
DROP TABLE IF EXISTS ward_services CASCADE;
DROP TABLE IF EXISTS ward CASCADE;

-- create tables

CREATE TABLE ward (
    ward_number INTEGER PRIMARY KEY,
    ward_name VARCHAR(100),
);

COMMENT ON TABLE ward IS 'Referential table - all characteristics will reference this table.';
COMMENT ON TABLE ward.ward_number IS 'Primary key: Ward number 1-14.';

CREATE TABLE election (
    election_id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    election_type VARCHAR(50),
    election_date DATE,
    UNIQUE(year, election_type)
);

COMMENT ON TABLE election IS 'Individual election events are represented in this table.'

CREATE TABLE race (
    race_id SERIAL PRIMARY KEY,
    election_id INTEGER NOT NULL REFERENCES election(election_id),
    type VARCHAR(50) NOT NULL, -- mayor or councillor
    ward_number INTEGER REFERENCES ward(ward_number),
    UNIQUE(election_id, type, ward_number)
);

COMMENT ON TABLE race IS 'Individual races in an election event - mayor or councillor.'
COMMENT ON COLUMN race.ward_number IS 'NULL for city-wide mayoral race, specific wards for councillor.'