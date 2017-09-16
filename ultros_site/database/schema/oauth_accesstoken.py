from sqlalchemy import Column, Integer, String, ARRAY, ForeignKey
from sqlalchemy.orm import relationship

from ultros_site.database.common import DeclarativeBase

__author__ = "Momo"


class OauthAccessToken(DeclarativeBase):
    __tablename__ = "oauth_accesstoken"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="oauth_tokens")
    scopes = Column(ARRAY(String))
