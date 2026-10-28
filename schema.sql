DROP TABLE IF EXISTS crops;

CREATE TABLE crops (
    id               SERIAL PRIMARY KEY,
    crop_name        TEXT    NOT NULL,
    ph_min           NUMERIC NOT NULL,
    ph_max           NUMERIC NOT NULL,
    moisture_min     NUMERIC NOT NULL,
    moisture_max     NUMERIC NOT NULL,
    soil_type        TEXT    NOT NULL,
    temperature_min  NUMERIC NOT NULL,
    temperature_max  NUMERIC NOT NULL,
    rainfall_min     NUMERIC NOT NULL,
    rainfall_max     NUMERIC NOT NULL,
    location         TEXT    NOT NULL,
    month_start      INTEGER,
    month_end        INTEGER,
    nitrogen         NUMERIC,
    phosphorus       NUMERIC,
    potassium        NUMERIC
);

CREATE INDEX idx_crops_soil_type ON crops (soil_type);
CREATE INDEX idx_crops_location  ON crops (location);