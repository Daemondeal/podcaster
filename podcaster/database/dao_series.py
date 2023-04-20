from .db import get_connection


def add_series(
    user_id: str, title: str, category: str, description: str, image_path: str
) -> str:
    query = """
    INSERT INTO PodcastSeries(Author_UserID, Title, Category, Description, ImageFilename) 
    VALUES (?,?,?,?,?);
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (user_id, title, category, description, image_path))

    connection.commit()

    series_id = cursor.lastrowid
    cursor.close()

    assert series_id is not None

    return str(series_id)


def get_series_from_id(series_id: str):
    query = """
    SELECT 
        PodcastSeriesID, Title, Category, Description, ImageFilename,
        Users.Name AS AuthorName, Users.UserType AS AuthorType, Users.Email AS AuthorEmail, 
        Users.ProfileImageFilename AS AuthorImageFilename, Author_UserID 
    FROM PodcastSeries 
    INNER JOIN Users
        ON UserID = Author_UserID
    WHERE PodcastSeriesID=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (series_id,))
    db_series = cursor.fetchone()
    cursor.close()

    return db_series


def get_all_series_with_episode_count():
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
    GROUP BY PodcastSeriesID;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query)

    series = cursor.fetchall()

    cursor.close()

    return series


def get_series_with_episode_count_from_category(category: str):
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
    WHERE Category = ?
    GROUP BY PodcastSeriesID;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (category,))

    series = cursor.fetchall()

    cursor.close()

    return series


def update_series_info(series_id: str, title: str, category: str, description: str):
    query = """
    UPDATE PodcastSeries 
    SET Title=?, Category=?, Description=? 
    WHERE PodcastSeriesID=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (title, category, description, series_id))

    connection.commit()

    cursor.close()


def update_series_image(series_id: str, filename: str):
    query = """
    UPDATE PodcastSeries
    SET ImageFilename=? 
    WHERE PodcastSeriesID=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (filename, series_id))

    connection.commit()

    cursor.close()


def delete_series(series_id: str):
    query = """
    DELETE FROM PodcastSeries 
    WHERE PodcastSeriesID=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (series_id,))

    connection.commit()


def get_all_categories():
    query = """
    SELECT DISTINCT Category
    FROM PodcastSeries;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query)

    series = cursor.fetchall()

    cursor.close()
    return series
