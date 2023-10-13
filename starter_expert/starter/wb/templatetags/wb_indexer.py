from django import template
from datetime import datetime


register = template.Library()

@register.filter(name='get_dict_value')
def get_dict_value(value, key):
    return value.get(key)


@register.filter(name='get_dict_data')
def get_dict_data(dict, key):
    return dict.get(key).get('data')

@register.filter(name='get_dict_req_depth')
def get_dict_req_depth(dict, key):
    return dict.get(key).get('req_depth')


@register.filter(name='get_dict_frequency')
def get_dict_frequency(dict, key):
    return dict.get(key).get('frequency')

@register.filter(name='get_dict_cat')
def get_dict_cat(dict, key):
    return dict.get(key).get('cat')


@register.filter(name='get_dict_key_place')
def get_el_place(dict, key):
    return list(dict).index(key) + 1

@register.filter(name='get_last_day_el')
def get_last_day_el(dict, key):
    last_frequency_day = None
    ans = None

    for certain_date_info in dict[key]['data']:
        cur_date_str = certain_date_info['date']
        if cur_date_str:
            cur_date = datetime.strptime(cur_date_str, "%m/%d/%y")
            if not last_frequency_day:
                last_frequency_day = cur_date
                ans = certain_date_info

            elif cur_date > last_frequency_day:
                last_frequency_day = cur_date
                ans = certain_date_info

        return ans['frequency'] if ans['frequency'] else ''
