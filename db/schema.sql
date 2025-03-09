CREATE TABLE novenas (
  stag_id BIGINT PRIMARY KEY,
  owner_address VARCHAR(42) NOT NULL,
  start_time TIMESTAMP NOT NULL,
  current_day INT DEFAULT 1,
  responses JSONB DEFAULT '{"1": null, "2": null, "3": null, "4": null, "5": null, "6": null, "7": null, "8": null, "9": null}'
);