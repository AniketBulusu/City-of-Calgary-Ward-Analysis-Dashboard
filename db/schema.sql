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
DROP TABLE IF EXISTS community_services CASCADE;
DROP TABLE IF EXISTS ward CASCADE;

-- create tables

CREATE TABLE ward (
    ward_number INTEGER PRIMARY KEY,
    ward_name VARCHAR(100)
);

COMMENT ON TABLE ward IS 'Referential table - all characteristics will reference this table.';
COMMENT ON COLUMN ward.ward_number IS 'Primary key: Ward number 1-14.';

CREATE TABLE election (
    election_id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    election_type VARCHAR(50),
    election_date DATE,
    UNIQUE(year, election_type)
);

COMMENT ON TABLE election IS 'Individual election events are represented in this table.';

CREATE TABLE race (
    race_id SERIAL PRIMARY KEY,
    election_id INTEGER NOT NULL REFERENCES election(election_id),
    type VARCHAR(50) NOT NULL, -- mayor or councillor
    ward_number INTEGER REFERENCES ward(ward_number),
    UNIQUE(election_id, type, ward_number)
);

COMMENT ON TABLE race IS 'Individual races in an election event - mayor or councillor.';
COMMENT ON COLUMN race.ward_number IS 'NULL for city-wide mayoral race, specific wards for councillor.';

CREATE TABLE candidate (
    candidate_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    party VARCHAR(100),
    UNIQUE(name)
);

COMMENT ON TABLE candidate IS 'Candidates running in elections are here.';

CREATE TABLE candidacy (
    candidate_id INTEGER NOT NULL REFERENCES candidate(candidate_id),
    race_id INTEGER NOT NULL REFERENCES race(race_id),
    PRIMARY KEY (candidate_id, race_id)
);

COMMENT ON TABLE candidacy IS 'Link between candidates to races.';

CREATE TABLE voting_station (
    station_code INTEGER PRIMARY KEY,
    ward_number INTEGER NOT NULL REFERENCES ward(ward_number),
    station_name VARCHAR(200),
    station_type VARCHAR(50) -- different types indicates in csv are advance, regular, etc.
);

COMMENT ON TABLE voting_station IS 'Physical voting locations, identifiable by ward.';

CREATE TABLE election_result (
    station_code INTEGER NOT NULL REFERENCES voting_station(station_code),
    candidate_id INTEGER NOT NULL REFERENCES candidate(candidate_id),
    race_id INTEGER NOT NULL REFERENCES race(race_id),
    votes INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (station_code, candidate_id, race_id)
);

COMMENT ON TABLE election_result IS 'Details on vote counts by station.';

CREATE TABLE ward_population (
    ward_number INTEGER PRIMARY KEY REFERENCES ward(ward_number),
    total INTEGER NOT NULL,
    density DECIMAL(10, 2),
    total_households INTEGER
);

COMMENT ON TABLE ward_population IS 'Ward population statistics.';

CREATE TABLE ward_income (
    ward_number INTEGER NOT NULL REFERENCES ward(ward_number),
    income_group VARCHAR(50) NOT NULL,
    household_count INTEGER NOT NULL,
    PRIMARY KEY (ward_number, income_group)
);

COMMENT ON TABLE ward_income IS 'Household income distribution by ward, by income group.';

CREATE TABLE ward_education (
    ward_number INTEGER NOT NULL REFERENCES ward(ward_number),
    education_level VARCHAR(100) NOT NULL,
    count INTEGER NOT NULL,
    percent DECIMAL(5, 2),
    PRIMARY KEY (ward_number, education_level)
);

COMMENT ON TABLE ward_education IS 'Education levels categorized by wards.';

CREATE TABLE ward_age_gender (
    ward_number INTEGER NOT NULL REFERENCES ward(ward_number),
    age_group VARCHAR(20) NOT NULL,
    male_count INTEGER NOT NULL,
    female_count INTEGER NOT NULL,
    total INTEGER NOT NULL,
    PRIMARY KEY (ward_number, age_group)
);

COMMENT ON TABLE ward_age_gender IS 'Population by age group and gender.';

CREATE TABLE ward_labour_force (
    ward_number INTEGER NOT NULL REFERENCES ward(ward_number),
    gender VARCHAR(10) NOT NULL,
    eligible INTEGER NOT NULL,
    in_labour_force INTEGER, 
    employed INTEGER, 
    self_employed INTEGER,
    unemployed INTEGER,
    not_in_labour_force INTEGER,
    participation_rate DECIMAL(5, 2),
    employment_rate DECIMAL(5, 2),
    unemployment_rate DECIMAL(5, 2),
    PRIMARY KEY (ward_number, gender)
);

COMMENT ON TABLE ward_labour_force IS 'Labour force statistics by ward and gender.';

CREATE TABLE ward_transport_mode (
    ward_number INTEGER NOT NULL REFERENCES ward(ward_number),
    transport_mode VARCHAR(50) NOT NULL,
    count INTEGER NOT NULL,
    percent DECIMAL(5, 2),
    PRIMARY KEY (ward_number, transport_mode)
);

COMMENT ON TABLE ward_transport_mode IS 'Mode of commute to work by ward';

CREATE TABLE ward_crime (
    ward_number INTEGER PRIMARY KEY REFERENCES ward(ward_number),
    total INTEGER NOT NULL,
    rate_per_1000 DECIMAL(6, 2) NOT NULL
);

COMMENT ON TABLE ward_crime IS 'Crime stats by ward.';

CREATE TABLE ward_disorder (
    ward_number INTEGER PRIMARY KEY REFERENCES ward(ward_number),
    total INTEGER NOT NULL,
    rate_per_1000 DECIMAL(6,2) NOT NULL
);

COMMENT ON TABLE ward_disorder IS 'Disorder incidence per ward.';

CREATE TABLE ward_transit_stops (
    ward_number INTEGER PRIMARY KEY REFERENCES ward(ward_number),
    total INTEGER NOT NULL,
    active INTEGER NOT NULL,
    inactive INTEGER
);

COMMENT ON TABLE ward_transit_stops IS 'Public transit stop counts by ward.';

CREATE TABLE ward_recreation (
    ward_number INTEGER NOT NULL REFERENCES ward(ward_number),
    facility_type VARCHAR(100) NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY (ward_number, facility_type)
);

COMMENT ON TABLE ward_recreation IS 'Recreation facilities by type and by ward.';

CREATE TABLE community_services (
    ward_number INTEGER NOT NULL REFERENCES ward(ward_number),
    service_type VARCHAR(100) NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY (ward_number, service_type)
);

COMMENT ON TABLE community_services IS 'Community service facilities by ward.';

