CREATE TABLE vinyl_genres (
    vinyl_id BIGINT NOT NULL REFERENCES vinyls(id) ON DELETE CASCADE,
    genre_id BIGINT NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (vinyl_id, genre_id)
);
