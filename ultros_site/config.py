from collections import defaultdict

import os

from ruamel.yaml import load


class Config:
    def __init__(self):
        self.config = {}

        if os.path.exists("config.yml"):
            self.config = load(open("config.yml"))

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        else:
            return self.config.get(item)

    def get(self, key, default=None):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            return self.config.get(key, default)

    @property
    def database_url(self):
        return os.getenv("DATABASE_URL", self.config.get("database_url"))

    @property
    def admin_username(self):
        return os.getenv("ADMIN_USERNAME", self.config.get("admin_username", "admin"))

    @property
    def recaptcha_secret(self):
        return os.getenv("RECAPTCHA_SECRET", self.config.get("recaptcha_secret"))

    @property
    def debug(self):
        return bool(os.getenv("DEBUG", self.config.get("debug")))

    @property
    def email(self):
        d = defaultdict(use=False, ssl=False)
        d.default_factory = lambda: None

        return d
