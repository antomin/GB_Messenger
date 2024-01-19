import logging
import re

logger = logging.getLogger("server")


class Descriptor:
    def __set_name__(self, owner, name):
        self.name = name


class Port(Descriptor):
    def __set__(self, instance, value):
        if 1023 > value > 65536:
            logger.critical(f"Try start server with wrong port <{value}>")
            raise ValueError(f"You cant start server with port <{value}>")
        instance.__dict__[self.name] = value


class IPAddress(Descriptor):
    def __set__(self, instance, value):
        if not re.match(r"([0-9]{1,3}[\.]){3}[0-9]{1,3}", value):
            logger.critical(f"Try start server with wrong address <{value}>")
            raise ValueError(f"You cant start server with address <{value}>")
        instance.__dict__[self.name] = value
