from django import template
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