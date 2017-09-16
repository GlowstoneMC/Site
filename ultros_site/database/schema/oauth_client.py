from sqlalchemy import Column, Integer, String, ARRAY, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ultros_site.database.common import DeclarativeBase

__author__ = "Momo"

class OauthClient(DeclarativeBase):
    __tablename__ = "oauth_client"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="oauth_clients")
    application_id = Column(String)
    # the scopes specified by the request; if a scope specified here is not in the app's defined scopes, it will be rejected
    scopes = Column(ARRAY(String), default=["user:username"])
    # if not present, the redirect_uri will default to the app's default
    redirect_uri = Column(String, default="")
    # when authorized, authorization_code will have a value
    authorization_code = Column(String, default="")
