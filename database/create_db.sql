CREATE TABLE Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserType VARCHAR(255) NOT NULL,
    Name VARCHAR(255) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    ProfileImageFilename VARCHAR(255) NOT NULL
);


CREATE TABLE PodcastSeries (
    PodcastSeriesID INTEGER PRIMARY KEY AUTOINCREMENT,
    Author_UserID INTEGER NOT NULL,
    Title VARCHAR(255) NOT NULL,
    Category VARCHAR(255) NOT NULL,
    ImageFilename VARCHAR(255) NOT NULL,
    Description TEXT NOT NULL,

    FOREIGN KEY (Author_UserID) REFERENCES Users(UserID) 
        ON DELETE CASCADE
);

CREATE TABLE PodcastEpisodes (
    PodcastEpisodeID INTEGER PRIMARY KEY AUTOINCREMENT,
    Series_PodcastSeriesID INTEGER NOT NULL,
    Title VARCHAR(255) NOT NULL,
    Description TEXT NOT NULL,
    DateInserted TIMESTAMP NOT NULL,
    TrackFilename VARCHAR(255) NOT NULL,
    TrackDuration INTEGER NOT NULL,

    UNIQUE (PodcastEpisodeID, Series_PodcastSeriesID),

    FOREIGN KEY (Series_PodcastSeriesID) REFERENCES PodcastSeries(PodcastSeriesID) 
        ON DELETE CASCADE
);

CREATE TABLE Comments(
    CommentID INTEGER PRIMARY KEY AUTOINCREMENT,
    Series_PodcastSeriesID INTEGER NOT NULL,
    Episode_PodcastEpisodeID INTEGER NOT NULL,
    Author_UserID INTEGER NOT NULL,
    Content TEXT NOT NULL,
    DateInserted TIMESTAMP NOT NULL,

    FOREIGN KEY (Series_PodcastSeriesID, Episode_PodcastEpisodeID) REFERENCES PodcastEpisodes(Series_PodcastSeriesID, PodcastEpisodeID) 
        ON DELETE CASCADE,
    FOREIGN KEY (Author_UserID) REFERENCES Users(UserID) 
        ON DELETE CASCADE
);

CREATE TABLE UserFollows(
    UserID INTEGER,
    PodcastSeriesID INTEGER,

    PRIMARY KEY (UserID, PodcastSeriesID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID) 
        ON DELETE CASCADE,
    FOREIGN KEY (PodcastSeriesID) REFERENCES PodcastSeries(PodcastSeriesID)
        ON DELETE CASCADE
);