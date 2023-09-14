import json
import re

from pprint import pprint
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from django.conf import settings

# Увеличиваем кэш регулярных выражений 
# для ускорения их работы
re._MAXCACHE = 3000

class OzonException(Exception):
    pass


class OzonQueryDepthException(OzonException):

    def __init__(self):
        super().__init__(
            "Недопустимая глубина запроса. Глубина должна быть не меньше 1"
        )


class OzonNotHaveProxiesException(OzonException):

    def __init__(self):
        super().__init__(
            "Не найдены прокси. Поменяйте параметр settings.ONLY_PROXY"
        )

class YandexVerification(OzonException):
    pass


def filtering_by_description_and_characteristics(dictionary):
    """Удаляет лишние json значения"""
    new_dictionary = {"description": [], "characteristics": [], "seller": []}

    for k, v in dictionary["widgetStates"].items():
        if "webDescription" in k:
            new_dictionary["description"].append(json.loads(v))
        elif "webCharacteristics" in k:
            new_dictionary["characteristics"].append(json.loads(v))
        elif "webCurrentSeller" in k:
            new_dictionary["seller"].append(json.loads(v))

    return new_dictionary


class OzonProductItem:

    _title: str = None
    _brand: str = None
    _nmid: int = None
    _brand_id: int = None
    _seller_id: int = None
    _characteristics: str = None
    _descriptions: str = None

    _brand_id_regex = re.compile(r"-(\d+)/")

    def __init__(self, json):
        self.dictionary = filtering_by_description_and_characteristics(json)
        self.json = json

    def _initializate_title(self):
        """Достает из dictionary название товара"""
        characteristics_list = self.dictionary['characteristics']
        title = None

        for characteristics in characteristics_list:
            try:
                title = characteristics['productTitle'].replace("Характеристики:", "")
            except KeyError:
                pass

        self._title = title
        return title

    def _initializate_seller_id(self):
        self._seller_id = self.dictionary['seller'][0]['id']
        return self._seller_id

    def _initializate_characteristics(self):
        characteristics_list = self.dictionary['characteristics']
        characteristics_result = []
        for characteristics in characteristics_list:
            shorts = characteristics['characteristics']

            for short in shorts:
                for character in short['short']:
                    name = character['name']
                    values = character['values']
                    characteristics_result.append(name)
                    for value in values:
                        characteristics_result.append(value['text'])

        self._characteristics = characteristics_result
        return characteristics_result

    def _initializate_brand(self):
        characteristics_list = self.dictionary['characteristics']
        brand = None
        for characteristics in characteristics_list:
            shorts = characteristics['characteristics']

            for short in shorts:
                for character in short['short']:
                    if character['key'] == 'Brand':
                        brand = character['values'][0]['link']

            if brand is not None:
                break


        self._brand = brand
        return brand

    def _initializate_descriptions(self):
        descriptions_list = self.dictionary['description']
        descriptions_result = []
        for description in descriptions_list:
            try:
                for character in description['characteristics']:
                    descriptions_result.append(character['content'])
                    descriptions_result.append(character['title'])
            except KeyError:
                pass
            try:
                rich_annotation = description.get('richAnnotationJson')
                if rich_annotation is not None:
                    for data in rich_annotation['content']:
                        for desc in data['text']['content']:
                            descriptions_result.append(desc)
                else:
                    descriptions_result.append(description['richAnnotation'])
            except KeyError:
                pass
        self._description = descriptions_result
        return descriptions_result

    def _initializate_nmid(self):
        raise NotImplemented

    @property
    def seller_id(self):
        if self._seller_id is None:
            return self._initializate_seller_id()
        return self._seller_id

    @property
    def title(self):
        if self._title is None:
            return self._initializate_title()
        return self._title

    @property
    def brand(self):
        if self._brand is None:
            return self._initializate_brand()
        return self._brand

    @property
    def nmid(self):
        if self._nmid is None:
            return self.initializate_nmid()
        return self._nmid

    @property
    def characteristics(self):
        if self._characteristics is None:
            return self._initializate_characteristics()
        return self._characteristics

    @property
    def descriptions(self):
        if self._descriptions is None:
            return self._initializate_descriptions()
        return self._descriptions

    @property
    def brand_id(self):
        if self.brand is not None:
            result = self._brand_id_regex.search(self.brand)
            if result is None:
                return None
            else:
                return result.group(1)
        else:
            return None

    def split(self):
        return \
            (self.title or "") + " " +\
            " ".join(self.characteristics) + \
            " ".join(self.descriptions)


class OzonPageItem:

    _top_category_regex = re.compile(r'в *категории* <a +href="(?:&#x2F;|/)category(?:&#x2F;|/)[^"]*-\d+(?:&#x2F;|/)[^>]*>([^<]*)</a>([^<]*)<')
    _req_depth_regex = re.compile(r'найден(?:о|) +(\d+) +товар')
    _redirect_regex = re.compile(r'location\.replace\( *"(.*)" *\);')
    _tf_state_regex = re.compile(r'(?:&|\?)tf_state=([-a-zA-Z0-9%_]+)')

    _nothing = None
    _redirect_url = None

    def __init__(self, html):
        self.html = html

    def nothing(self):
        if self._nothing is None:
            self._nothing = "searchResultsError" in self.html
        return self._nothing

    def links_query_page(self):
        if not self.nothing():
            soup = BeautifulSoup(self.html, 'html.parser')
            result = []
            tag_data = soup.find(class_='client-state').find_all('div', {'id': products_filter_tag})
            for t_data in tag_data:
                data = json.loads(t_data['data-state'])
                try: 
                    for d in data['items']:
                        result.append(d['action']['link'])
                except KeyError:
                    pass

            return result
        else:
            return []

    def _check_redirect_url(self):
        redirect_regex_result = self._redirect_regex.search(self.html)

        if redirect_regex_result is None:
            self._redirect_url = None
        else:
            self._redirect_url = redirect_regex_result.group(1).replace(r"\/", "/").encode().decode('unicode-escape')
            
    @property
    def req_depth(self):
        """Возвращает глубину выдачи"""
        if not self.nothing():
            regex_req_depth = self._req_depth_regex.search(self.html.replace(u"\u2009", ""))
            req_depth = regex_req_depth.group(1)
            return int(req_depth)
        else:
            return 0

    @property
    def top_category(self):
        """Возвращает топовую категорию"""
        if not self.nothing():
            searched_top_category = self._top_category_regex.search(self.html)

            if searched_top_category is None:
                return None
            else:
                return searched_top_category.group(1)
        else:
            return None

    @property
    def tf_state(self):
        if not self.nothing():
            try:
                result = self._tf_state_regex.search(self.html)
                return result.group(1)
            except AttributeError:
                return None
        else:
            return None

    @property
    def redirect_url(self):
        if not self._redirect_url:
            self._check_redirect_url()
        return self._redirect_url

    def is_redirect_page(self):
        """Проверяет является ли страница 
        перенаправляемой (выдающая 300-ую)"""
        if not self._redirect_url:
            self._check_redirect_url()
        return self._redirect_url is not None


def proxies_generator(proxies):
    """Прокси генератор. Последовательное использование прокси"""
    if len(proxies) == 0 and settings.ONLY_PROXY:
        raise OzonNotHaveProxiesException()

    while True:
        yield from iter(proxies)

        if not settings.ONLY_PROXY:
            yield {}


def products_filter_tag(id):
    return "state-searchResults" in (id or "")


def get_query_headers():
    return {
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':
        'gzip, deflate, br',
        'Accept-Language':
        'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control':
        'max-age=0',
        'Sec-Ch-Ua':
        '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'Sec-Ch-Ua-Mobile':
        '?0',
        'Sec-Ch-Ua-Platform':
        '"Windows"',
        'Sec-Fetch-Dest':
        'document',
        'Sec-Fetch-Mode':
        'navigate',
        'Sec-Fetch-Site':
        'same-origin',
        'Sec-Fetch-User':
        '?1',
        'Upgrade-Insecure-Requests':
        '1',
        #'Reference':
        #'https://www.ozon.ru/search/?',
        'Cookie':
        'adult_user_birthdate=2000-03-03',
        'User-Agent':
        UserAgent().chrome,
    } 


def get_api_headers():
    return {
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':
        'gzip, deflate, br',
        'Accept-Language':
        'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control':
        'max-age=0',
        'Sec-Ch-Ua':
        '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'Sec-Ch-Ua-Mobile':
        '?0',
        'Sec-Ch-Ua-Platform':
        '"Windows"',
        'Sec-Fetch-Dest':
        'document',
        'Sec-Fetch-Mode':
        'navigate',
        'Sec-Fetch-Site':
        'none',
        'Sec-Fetch-User':
        '?1',
        'Upgrade-Insecure-Requests':
        '1',
}


def filtering_price(json_price):
    widgets = json_price['widgetStates']

    for key, value in widgets.items():
        if "webPrice" in key:
            json_value = json.loads(value)
            try:
                return int(json_value['cardPrice'].replace("\u2009", "").replace("₽", ""))
            except KeyError:
                return int(json_value['price'].replace("\u2009", "").replace("₽", ""))
        elif "error" in key:
            return None