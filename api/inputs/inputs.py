''' Input Validation Classes '''
from api.validations import Validations
# Registration validations
REGISTER_RULES = [
    {'username': [('string', True), ('minimum', 1),
                  ('maximum', 30), ('required', True)]},
    {'email': [('minimum', 6), ('maximum', 30),
               ('required', True), ('email', True)]},
    {'password': [('minimum', 6), ('maximum', 30), ('required', True)]},
    {'confirm_password': [('minimum', 6), ('maximum', 30),
                          ('required', True), ('same', 'password')]},
]
# Login validation
LOGIN_RULES = [
    {'email': [('minimum', 6), ('maximum', 30),
               ('required', True), ('email', True)]},
    {'password': [('minimum', 6), ('required', True)]},
]
# Change password validations
CHANGE_PWD_RULES = [
    {'new_password': [('minimum', 6), ('maximum', 30), ('required', True)]},
    {'old_password': [('minimum', 6), ('maximum', 30), ('required', True)]},
]
# Reset password validations
RESET_PWD_RULES = [
    {'email': [('minimum', 6), ('maximum', 30),
               ('required', True), ('email', True)]},
    {'password': [('minimum', 6), ('maximum', 30), ('required', True)]},
    {'confirm_password': [('minimum', 6), ('maximum', 30),
                          ('required', True), ('same', 'password')]},
]
# Reset password validations
CONFIRM_EMAIL_RULES = [
    {'email': [('required', True), ('minimum', 6),
               ('maximum', 100), ('email', True)]}
]
CONFIRM_TOKEN_RULES = [
    {'token': [('required', True), ('minimum', 6),
               ('maximum', 100)]}
]
# Reset password validations
RESET_LINK_RULES = [
    {'email': [('minimum', 6), ('maximum', 30),
               ('required', True), ('email', True)]}
]
# Register business validation rules
REGISTER_BUSINESS_RULES = [
    {'name': [('minimum', 2), ('required', True)]},
    {'description': [('minimum', 6), ('required', True)]},
    {'category': [('minimum', 1), ('required', True)]},
    {'country': [('minimum', 1), ('required', True)]},
    {'city': [('minimum', 1), ('required', True)]},
]
REVIEW_RULES = [
    {'review': [('minimum', 4), ('maximum', 250), ('required', True)]},
]


def validate(inputs, all_rules):
    ''' Register validation method '''
    error_bag = {}
    valid = Validations(inputs)
    for rules in all_rules:
        for key in rules:
            rule_key = key
            for rule in rules[rule_key]:
                execute = getattr(valid, rule[0])(
                    rule_key, rule[1])
                if execute is True:
                    pass
                if execute is not True:
                    if rule_key in error_bag:
                        error_bag[rule_key].append(execute)
                    else:
                        error_bag[rule_key] = []
                        error_bag[rule_key].append(execute)
    if len(error_bag) is not 0:
        return error_bag
    return True
