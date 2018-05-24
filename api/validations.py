"""
Validations Methods Class
"""

import re
from api import db
from api.models.user import User


class Validations():
    """Validations class"""

    def __init__(self, all_inputs):
        """ All inputs dictionary should be available to the class"""
        self.all = all_inputs

    def string(self, key, string):
        """Check if input is required"""
        if key in self.all and self.all[key] is not None:
            if not re.match(r"[^[a-zA-Z0-9]+$", self.all[key]):
                return True
            return key + " should be string"
        return True

    def minimum(self, key, minimum):
        """Check required character size"""
        if key in self.all and self.all[key] is not None:
            if len(self.all[key]) < int(minimum):
                return key + " should not be less than " + str(minimum) + " characters"
            return True
        return True

    def maximum(self, key, maximum):
        """Check required character size"""
        if key in self.all and self.all[key] is not None:
            if len(self.all[key]) > int(maximum):
                return key + " should not be greater than " + str(maximum) + " characters"
            return True
        return True

    def email(self, key, email):
        """Check required character size"""
        if key in self.all:
            if not re.match(r"[^@\s]+@[^@\s]+\.[a-zA-Z]+$", self.all[key]):
                return "Invalid email address"
            return True
        return True

    def same(self, key, same):
        """Check if given """
        if key in self.all and same in self.all:
            if self.all[same] != self.all[key]:
                return same + " don't match"
            return True
        return True

    def required(self, key, is_required=True):
        """Check input it is required"""
        if key in self.all:
            if self.all[key] is None:
                return key + " should not be empty"
            return True
        return key + " is required"

    def unique(self, key, tableRow):
        """Check if value is unique"""
        model = tableRow.split(':')[0]
        row = tableRow.split(':')[1]
        if key in self.all:
            if ((db.session.query((eval(model)).id).filter(getattr((eval(model)), row) == self.all[key]).scalar()) is not None):
                return row+" has been taken"
            return True
        return True
