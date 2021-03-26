import re
import json

class Source:
    def __init__(self, redis):
        self.redis = redis

    ###########
    # Utilities
    ###########

    RE_PHONE_COUNTRY_CODE = re.compile(r'^\+1? ')
    RE_PHONE_DISALLOWED_CHARACTERS = re.compile(r'[A-Za-z\(\) \-\.]')

    def clean_phone(self, phone):
        if not phone:
            return phone
        if type(phone) == int:
            phone = str(phone)
        phone = self.RE_PHONE_COUNTRY_CODE.sub('', phone)
        phone = self.RE_PHONE_DISALLOWED_CHARACTERS.sub('', phone)
        if phone in ('1111111111'):
            return None
        return phone

    ###############
    # Scraping flow
    ###############

    new_people = None
    people = None

    def scrape(self, current_people):
        """
        Read all people from this source and store to new_people.
        """
        raise NotImplementedError

    def pull(self, current_people):
        """
        Read data from this source, either through redis cache or by scraping.
        """
        redis_key = 'scraped_data.' + self.__class__.__name__
        current_cache = self.redis.get(redis_key)
        if current_cache:
            return json.loads(current_cache)
        else:
            scraped_data = self.scrape(current_people)
            self.redis.set(redis_key, json.dumps(scraped_data))
            return scraped_data

    def merge(self, current_people):
        """
        Given list of people from previous sources, merge in newly scraped people.
        :param current_people: list of people scraped from previous sources.
        :param new_people: list of new people scraped from this source.
        """
        return current_people + self.new_people
