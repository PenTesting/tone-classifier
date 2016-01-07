#!/usr/bin/python

import psycopg2
import json

class Lexicon:

    @staticmethod
    def to_unicode(s):
        if isinstance(s, str):
            return unicode(s, 'utf-8')
        elif isinstance(s, unicode):
            return s

    def get_name(self):
        return self.name

    def get_tone_from_table(self, unicode_term):
        cursor = self.connection.cursor()
        cursor.execute("""SELECT {result} FROM {table} WHERE
            {column}=\'{value}\'""".format(result = self.value_column_name,
            table = self.table, column = self.term_column_name,
            value = unicode_term.encode('utf-8')))

        result = cursor.fetchone()
        if not (result is None):
            result = result[0]
        return result

    def get_tone(self, term):
        unicode_term = Lexicon.to_unicode(term)
        tone = 0

        invert_tone = False
        if (unicode_term[0] == '-'):
            unicode_term = unicode_term[1:]
            invert_tone = True
        elif (unicode_term[0] == '+'):
            unicode_term = unicode_term[1:]

        if (unicode_term in self.cache):
            tone = self.cache[unicode_term]
        else:
            result = self.get_tone_from_table(unicode_term)
            if not (result is None):
                tone = float(result)
                self.cache[unicode_term] = tone

        # invert term tonality in case of negative mark '-'
        if (invert_tone):
            tone *= -1

        return tone

    def __init__(self, configpath, table, name,
        term_column_name, value_column_name):

        self.cache = {}

        # init config file
        with open(configpath, "r") as f:
            settings = json.load(f, encoding='utf-8')

        # init connection settings
        connection_settings = "dbname=%s user=%s password=%s host=%s"%(
            settings['database'], settings["user"], settings["password"],
            settings["host"])
        self.connection = psycopg2.connect(connection_settings)

        # init lexicon parameters
        self.name = name
        self.table = table
        self.term_column_name = term_column_name
        self.value_column_name = value_column_name