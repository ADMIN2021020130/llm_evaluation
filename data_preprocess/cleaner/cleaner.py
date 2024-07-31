import os
import logging


class BaseCleaner:
    def __init__(self, config):
        pass

    def clean(self, data_flow):
        data_flow.cleaned_data = data_flow.sampled_data

def get_cleaner(cleaner_name, config):
    if cleaner_name =="base":
        return BaseCleaner(config)
    else:
        return None