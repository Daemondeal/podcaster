from .db import get_connection


def add_creator(
    username: str, profile_image_filename: str, email: str, hashed_password: str
) -> str:
    query = """
    INSERT INTO Users(UserType, Name, Password, ProfileImageFilename, Email) 
    VALUES (?,?,?,?,?);
    """

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        query, ("Creator", username, hashed_password, profile_image_filename, email)
    )

    connection.commit()

    userid = cursor.lastrowid
    cursor.close()

    assert userid is not None

    return str(userid)


def add_listener(
    username: str, profile_image_filename: str, email: str, hashed_password: str
) -> str:
    query = """
    INSERT INTO Users(UserType, Name, Password, ProfileImageFilename, Email) 
    VALUES (?,?,?,?,?);
    """

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        query, ("Listener", username, hashed_password, profile_image_filename, email)
    )

    connection.commit()

    userid = cursor.lastrowid
    cursor.close()

    assert userid is not None

    return str(userid)


def get_user_from_id(user_id: str):
    query = """
    SELECT UserID, UserType, Name, Email, ProfileImageFilename 
    FROM Users 
    WHERE UserID=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (user_id,))

    db_user = cursor.fetchone()
    cursor.close()

    return db_user


def get_user_and_password_from_email(email: str):
    query = """
    SELECT UserID, UserType, Name, Email, ProfileImageFilename, Password 
    FROM Users 
    WHERE Email=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (email,))

    db_user = cursor.fetchone()
    cursor.close()

    return db_user


def get_follows_from_user(userid: str):
    query = """
    SELECT 
        PodcastSeries.PodcastSeriesID, PodcastSeries.Title, Category, PodcastSeries.Description, ImageFilename, 
        Users.Name AS AuthorName, Users.UserType AS AuthorType, 
        Users.Email AS AuthorEmail, Users.ProfileImageFilename AS AuthorImage, Users.UserID AS Author_UserID,
        COUNT(PodcastEpisodeID) AS EpisodeCount
    FROM PodcastSeries
    INNER JOIN UserFollows
        ON UserFollows.PodcastSeriesID = PodcastSeries.PodcastSeriesID
    LEFT JOIN PodcastEpisodes
        ON Series_PodcastSeriesID = PodcastSeries.PodcastSeriesID
    INNER JOIN Users
        ON Users.UserID = PodcastSeries.Author_UserID
    WHERE UserFollows.UserID = ?
    GROUP BY PodcastSeries.PodcastSeriesID;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (userid,))

    follows = cursor.fetchall()
    cursor.close()

    return follows


def get_series_from_user(userid: str):
    query = """
    SELECT 
        PodcastSeriesID, PodcastSeries.Title, Category, PodcastSeries.Description, ImageFilename, 
        Users.Name AS AuthorName, Users.UserType AS AuthorType, Users.Email AS AuthorEmail, 
        Users.ProfileImageFilename AS AuthorImage, Author_UserID,
        COUNT(PodcastEpisodeID) AS EpisodeCount
    FROM PodcastSeries
    LEFT JOIN PodcastEpisodes
        ON Series_PodcastSeriesID = PodcastSeriesID
    INNER JOIN Users
        ON UserID = Author_UserID
    WHERE Author_UserID = ?
    GROUP BY PodcastSeriesID;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (userid,))
    series = cursor.fetchall()

    cursor.close()

    return series


def is_user_following_series(user_id: str, series_id: str) -> bool:
    query = """
    SELECT * 
    FROM UserFollows 
    WHERE PodcastSeriesID=? AND UserID=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (series_id, user_id))

    does_follow = cursor.fetchone() is not None
    cursor.close()

    return does_follow


def is_user_owner_of_series(user_id: str, series_id: str) -> bool:
    query = """
    SELECT * 
    FROM PodcastSeries 
    WHERE PodcastSeriesID=? AND Author_UserID=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (series_id, user_id))

    does_follow = cursor.fetchone() is not None
    cursor.close()

    return does_follow


def add_user_follow(userid: str, seriesid: str):
    query = """
    INSERT INTO UserFollows(UserID, PodcastSeriesID) 
    VALUES (?,?);
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (userid, seriesid))

    connection.commit()

    cursor.close()


def delete_user_follow(userid: str, seriesid: str):
    query = """
    DELETE FROM UserFollows 
    WHERE UserID=? AND PodcastSeriesId=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (userid, seriesid))

    connection.commit()

    cursor.close()


def is_email_taken(email: str) -> bool:
    query = """
    SELECT * 
    FROM Users 
    WHERE Email=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (email,))

    user_exists = cursor.fetchone() is not None

    cursor.close()
    return user_exists
