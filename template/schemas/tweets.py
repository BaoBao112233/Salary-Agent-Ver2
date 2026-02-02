from typing import Optional, List

from pydantic import BaseModel


class TweetSchema(BaseModel):
    tweet_id: str
    user_id: str
    user_name: str
    quote_id: Optional[str] = None
    retweet_id: Optional[str] = None
    reply_id: Optional[str] = None
    content: str
    lang: str
    created_date: int
    view_count: int
    favorite_count: int
    quote_count: int
    reply_count: int
    retweet_count: int
    hash_tags: Optional[List[str]] = None
    cash_tags: Optional[List[str]] = None
    symbols: Optional[List[str]] = None
    urls: Optional[List[str]] = None
    user_mentions: Optional[List[str]] = None
    images: Optional[List[str]] = None  # List of image ids


class UserSchema(BaseModel):
    user_id: str
    user_name: str
    name: str
    bio: Optional[str] = None
    joined_date: int
    follower_count: int
    following_count: int
    favourite_count: int
    status_count: int
    verified: bool
    verified_follower_count: int
    followers: Optional[List[str]] = None  # List of user ids
    following: Optional[List[str]] = None  # List of user ids
