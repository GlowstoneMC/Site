# coding=utf-8
from sqlalchemy import Column, Integer, String, ARRAY

from ultros_site.database.common import DeclarativeBase

__author__ = "Momo"


class OauthApplication(DeclarativeBase):
    __tablename__ = "oauth_application"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    display_name = Column(String)
    display_description = Column(String)
    display_icon = Column(String)

    app_id = Column(String, unique=True)
    app_secret = Column(String, unique=True)
    redirect_uri = Column(String)

    # default scopes, may be: user:username, user:email, user:type, user:verified, user:profile
    scopes = Column(ARRAY(String), default=["user:username"])

    def __repr__(self):
        return "<{}(id={}, name={}, display_name={}, display_description={}, display_icon={}, app_id={}, " \
               "redirect_uri={}>".format(
            self.__class__.__name__,
            self.id,
            self.name,
            self.display_name,
            self.display_description,
            self.display_icon,
            self.app_id,
            self.redirect_uri
        )
