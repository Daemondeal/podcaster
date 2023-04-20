from .db import get_connection

from datetime import datetime, date


def add_episode(
    series_id: str,
    title: str,
    description: str,
    date: datetime,
    track_name: str,
    duration: float,
) -> str:
    query = """
    INSERT INTO PodcastEpisodes(Series_PodcastSeriesID, Title, Description, DateInserted, TrackFilename, TrackDuration) 
    VALUES (?,?,?,?,?,?);
    """

    connection = get_connection()
    cursor = connection.cursor()

    duration_seconds = int(round(duration))

    cursor.execute(
        query, (series_id, title, description, date, track_name, duration_seconds)
    )

    connection.commit()

    episodeid = cursor.lastrowid
    cursor.close()

    assert episodeid is not None

    return str(episodeid)


def get_episode_from_id(series_id: str, episode_id: str):
    query = """
    SELECT 
        PodcastEpisodeID, PodcastEpisodes.Title, PodcastSeries.Title AS SeriesTitle, Series_PodcastSeriesID, 
        PodcastEpisodes.Description, DateInserted, TrackFilename
    FROM PodcastEpisodes
        INNER JOIN PodcastSeries
        ON Series_PodcastSeriesID = PodcastSeriesID
    WHERE PodcastSeriesID=? AND PodcastEpisodeID=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (series_id, episode_id))

    episode = cursor.fetchone()
    cursor.close()

    return episode


def get_episodes_from_series(series_id: str):
    query = """
    SELECT 
        PodcastEpisodeID, PodcastEpisodes.Title, PodcastEpisodes.Description, 
        PodcastEpisodes.DateInserted, PodcastEpisodes.Series_PodcastSeriesID,
        Count(Comments.Content) as CommentsAmount, TrackDuration
    FROM PodcastEpisodes
    LEFT JOIN Comments
        ON Episode_PodcastEpisodeID = PodcastEpisodeID
    WHERE PodcastEpisodes.Series_PodcastSeriesID = ?
    GROUP BY PodcastEpisodeID
    ORDER BY PodcastEpisodes.DateInserted DESC;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (series_id,))
    episodes = cursor.fetchall()

    cursor.close()

    return episodes


def get_episodes_from_series_before_date(series_id: str, date: date):
    query = """
    SELECT 
        PodcastEpisodeID, PodcastEpisodes.Title, PodcastEpisodes.Description, 
        PodcastEpisodes.DateInserted, PodcastEpisodes.Series_PodcastSeriesID,
        Count(Comments.Content) as CommentsAmount, TrackDuration
    FROM PodcastEpisodes
    LEFT JOIN Comments
        ON Episode_PodcastEpisodeID = PodcastEpisodeID
    WHERE PodcastEpisodes.Series_PodcastSeriesID = ? AND date(PodcastEpisodes.DateInserted) <= ?
    GROUP BY PodcastEpisodeID
    ORDER BY PodcastEpisodes.DateInserted DESC;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (series_id, date))
    episodes = cursor.fetchall()

    cursor.close()

    return episodes


def update_episode_info(
    series_id: str,
    episode_id: str,
    title: str,
    description: str,
    date: datetime,
):
    query = """
    UPDATE PodcastEpisodes 
    SET Title=?, Description=?, DateInserted=? 
    WHERE Series_PodcastSeriesID=? AND PodcastEpisodeID=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (title, description, date, series_id, episode_id))

    connection.commit()


def update_episode_track(
    series_id: str, episode_id: str, track_name: str, duration: float
):
    query = """
    UPDATE PodcastEpisodes 
    SET TrackFilename=?, TrackDuration=? 
    WHERE Series_PodcastSeriesID=? AND PodcastEpisodeID=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    duration_seconds = int(round(duration))

    cursor.execute(query, (track_name, duration_seconds, series_id, episode_id))

    connection.commit()


def delete_episode(series_id: str, episode_id: str):
    query = """
    DELETE FROM PodcastEpisodes 
    WHERE Series_PodcastSeriesID=? AND PodcastEpisodeID=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (series_id, episode_id))

    connection.commit()


def add_comment(
    userid: str, seriesid: str, episodeid: str, content: str, date: datetime
) -> str:
    query = """
    INSERT INTO Comments(Series_PodcastSeriesID, Episode_PodcastEpisodeID, Author_UserID, Content, DateInserted) 
    VALUES (?,?,?,?,?);
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (seriesid, episodeid, userid, content, date))

    connection.commit()

    commentid = cursor.lastrowid
    cursor.close()

    assert commentid is not None

    return str(commentid)


def get_comments_from_episode(seriesid: str, episodeid: str):
    query = """
    SELECT CommentID, Content, Author_UserID, Users.Name AS AuthorName, Users.ProfileImageFilename AS AuthorImage, DateInserted
    FROM Comments 
    INNER JOIN Users
        ON Users.UserID = Author_UserID
    WHERE Episode_PodcastEpisodeID=? AND Series_PodcastSeriesID=?
    ORDER BY DateInserted DESC;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (episodeid, seriesid))
    comments = cursor.fetchall()
    cursor.close()

    return comments


def update_comment(commentid: str, content: str):
    query = """
    UPDATE Comments 
    SET Content=? 
    WHERE CommentID=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (content, commentid))

    connection.commit()

    cursor.close()


def delete_comment(commentid: str):
    query = """
    DELETE FROM Comments 
    WHERE CommentID=?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (commentid,))

    connection.commit()
    cursor.close()


def is_comment_owned_by_user(userid: str, commentid: str):
    query = """
    SELECT * 
    FROM Comments 
    WHERE Author_UserID = ? AND CommentID = ?;
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(query, (userid, commentid))
    is_owner = cursor.fetchone() is not None

    cursor.close()

    return is_owner
