import pandas as pd
import os

class FlatFileHandler:
    def __init__(self, filename, delimiter=','):
        self.filename = filename
        self.delimiter = delimiter

    def read(self, columns=None):
        df = pd.read_csv(self.filename, delimiter=self.delimiter)
        if columns:
            df = df[columns]
        return df
