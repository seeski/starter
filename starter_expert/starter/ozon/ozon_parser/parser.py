import asyncio
import json
import csv
import re
import time
import traceback
import functools
import logging
import pickle

from async_lru import alru_cache
from pprint import pprint
from curl_cffi.requests import AsyncSession
from urllib.parse import urlencode 
from bs4 import BeautifulSoup
from .utils import (
    proxies_generator,
    get_query_headers,
    get_api_headers,
    OzonQueryDepthException,
    OzonException,
    OzonPageItem,
    OzonProductItem,
    filtering_price
)
from django.conf import settings


proxies = proxies_generator(settings.PROXIES)
urls = []

logger = logging.getLogger("ozon_indexer")
"""

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logs.log')
stdout = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stdout.setFormatter(formatter)
logger.addHandler(stdout)
logger.addHandler(file_handler)
"""

class Checker:

    # при инициализации получаем nmid и описание
    # удаляем все знаки препинания из описания товара
    def __init__(self, nmid, desc):
        self.nmid = str(nmid)
        self.desc = set(
            re.sub(r' (?= )', ' ', re.sub(r'[^\w\s]', '', desc)).split(' ')
        )

    # находим совпадения в запросе и описание, также делаем проверку на длину запроса
    def check_desc(self, query):
        if set(query[0].split(' ')).issubset(self.desc) and len(query[0]) >= 3:
            return True
        else:
            return False

    # проверяет существование товара по опреденному запросу
    # если есть, то возвращается true и наоборот
    # метод используется в качестве аргумента для встроенной функции filter
    def check_existence(self, brand_ids):
        if self.nmid in brand_ids:
            return True
        else:
            return False

    # возвращает рекламное место товара
    def check_ad(self, ad_ids: list[str]):
        if self.nmid in ad_ids:
            return ad_ids.index(self.nmid) + 1
        else:
            return 0

    # проверяет место товара среди первых 10 страниц выдачи
    def checkFirstTenPages(self, ids):
        if self.nmid in ids:
            # индексация списков начинается с нуля
            # поэтому для получения места выдачи +1
            return ids.index(self.nmid) + 1
        else:
            return 0

    # возвращает имя топ категории
    def checkTopCategory(self, category_id, subject_base):
        if category_id in subject_base:
            return subject_base[category_id]
        else:
            return None


class BaseOzonParser(AsyncSession):
    """Базовый парсер озона. Возвращает
    чистые данные"""

    async def get_html_query_page(self, url):
        """Возвращает страницу по ссылке"""
        r = await self.get(
            url, 
            headers=get_query_headers(), 
            impersonate=settings.IMPERSONATE, 
            proxies=next(proxies)
        )
        logger.debug(url)
        return r.text


    async def get_full_info_from_api_product(self, link_or_nmid):
        """Получает полную информацию о продукте по api
        и возвращает json"""
        if issubclass(str, type(link_or_nmid)):
            raw_url 
            url = "https://www.ozon.ru/api/entrypoint-api.bx"\
                  "/page/json/v2?%s&layout_container=pdpPage"\
                  "2column&layout_page_index=2" %\
                  (urlencode({"url": link}),)

        elif issubclass(int, type(link_or_nmid)):
            url = "https://www.ozon.ru/api/entrypoint-api.bx"\
                  "/page/json/v2?url=/product/%s&layout_cont"\
                  "ainer=pdpPage2column&layout_page_index=2" %\
                  (link_or_nmid,)
        else:
            raise OzonException()

        r = await self.get(
            url, 
            headers=get_api_headers(), 
            impersonate=settings.IMPERSONATE, 
            proxies=next(proxies)
        )
        return r.json()

    async def get_price_product(self, link_or_nmid):
        if issubclass(str, type(link_or_nmid)):
            raw_url 
            url = "https://www.ozon.ru/api/entrypoint-api.bx"\
                  "/page/json/v2?%s" %\
                  (urlencode({"url": link}),)

        elif issubclass(int, type(link_or_nmid)):
            url = "https://www.ozon.ru/api/entrypoint-api.bx"\
                  "/page/json/v2?url=/product/%s/"\
                  % (link_or_nmid,)
        else:
            raise OzonException()

        r = await self.get(
            url,
            headers=get_api_headers(), 
            impersonate=settings.IMPERSONATE, 
            proxies=next(proxies)
        )

        price = filtering_price(r.json())
        return price


    async def get_query_page(
        self, 
        query, 
        page=1, 
        deny_category_prediction=False,
        tf_state=None,
        **params
    ):
        """Возвращает непрогруженную страницу запроса"""
        url = "https://www.ozon.ru/search/?%s" % urlencode(
            {
                "text": query, 
                "page": page, 
                "from_global": "true",
                # Параметр, отвечающий за 
                # отказа от редиректа в категорию
                # если товар как-то связан
                "deny_category_prediction": str(deny_category_prediction).lower(),
                **params
            } | ({} if tf_state is None else {"tf_state": tf_state})
        )
        html = await self.get_html_query_page(url)

        return html

    async def get_json_query_page(
        self,
        query,
        page=1,
        deny_category_prediction=False,
        **params,
    ):
        url = "https://www.ozon.ru/api/entrypoint-api.bx/page/json/v2?url=/search/?%s" % urlencode(
            {
                "text": query, 
                "page": page, 
                "from_global": "true",
                # Параметр, отвечающий за 
                # отказа от редиректа в категорию
                # если товар как-то связан
                "deny_category_prediction": str(deny_category_prediction).lower(),
                **params
            } 
        )
        r = await self.get_html_query_page(url)

        return r.json()


class AbstractOzonPageParser:

    def __init__(self, *args, **kwargs):
        pass

    async def initializate_url(self, url):
        pass

    async def get_query_page(self, query, page):
        pass

    def is_redirect_page(self):
        pass


class OzonRedirectPageParser(AbstractOzonPageParser):
    """Класс, представляющий собой парсинг ссылок товара
    на какой либо странице озона. Необходимо было
    реализовать редирект в случае его выдачи"""

    _top_category = None

    def __init__(self, session, query):
        self.session = session
        self.query = query

    @property
    def top_category(self):
        return self._top_category

    @property
    def req_depth(self):
        return self.first_item.req_depth

    async def initializate_url(self):
        """Блять, нужно чтобы проверить есть ли
        редирект ссылка в javascript коде. Если есть, 
        то url меняется на тот, который в js находится,
        и подставляются нужные значения"""
        url = "https://www.ozon.ru/search/?%s" % urlencode(
            {
                "text": self.query, 
                "page": 1, 
                "from_global": "true",
            } 
        )
        content = await self.session.get_html_query_page(url)
        item = OzonPageItem(content)

        self.is_redirect_page = item.is_redirect_page()

        if self.is_redirect_page:
            self.url = item.redirect_url.split("?")[0] + "?"
            self.first_item = await self.get_query_page(page=1, _get_first_item=True)
            self.url = item.redirect_url.split("?")[0] + f"?tf_state={self.first_item.tf_state}&"
            self._top_category = self.first_item.top_category
        else:
            self.first_item = item
            self.url = f"https://www.ozon.ru/search/?tf_state={self.first_item.tf_state}&"

        return self.first_item

    async def get_query_page(self, page=1, _get_first_item = False):
        if page == 1 and not _get_first_item:
            return self.first_item

        url = self.url + "%s" % urlencode(
            {
                "text": self.query, 
                "deny_category_prediction": "true",
                "category_was_predicted": "true",
                "from_global": "true",
            } | ({} if page == 1 else {"page": page})
        )
        item = OzonPageItem(await self.session.get_html_query_page(url))
        return item


class OzonNotRedirectPageParser(AbstractOzonPageParser):

    def __init__(self, session, query):
        self.session = session
        self.query = query

    @property
    def req_depth(self):
        return self.first_item.req_depth

    async def initializate_url(self):
        """Нихуя не делает, полиморфизм епт"""
        self.first_item = OzonPageItem(await self.session.get_query_page(self.query, page=1, deny_category_prediction=True))
        return self.first_item

    async def get_query_page(self, page):
        if page == 1:
            return self.first_item
        else:
            return OzonPageItem(await self.session.get_query_page(self.query, page=page, deny_category_prediction=True, tf_state=self.first_item.tf_state))


class OzonBrandSellerPageParser(AbstractOzonPageParser):


    def __init__(self, session, query, brand, seller):
        self.seller_id = seller
        self.brand_id = brand
        self.session = session
        self.query = query

    @property
    def req_depth(self):
        return self.first_item.req_depth

    async def initializate_url(self):
        url_encode = {
                "text": self.query, 
                "from_global": "true",
                "brand": self.brand_id,
                "seller": self.seller_id,
                "deny_category_prediction": True,
            } 
        if self.brand_id is not None:
            url_encode["brand"] = self.brand_id
        if self.seller_id is not None:
            url_encode["seller"] = self.seller_id

        self.first_item = OzonPageItem(
            await self.session.get_html_query_page("https://www.ozon.ru/search/?%s&page=1")
        )
        url_encode['tf_state'] = self.first_item.tf_state
        self.url = "https://www.ozon.ru/search/?%s" % urlencode(url_encode)

        return self.first_item

    async def get_query_page(self, page):
        if page == 1:
            return self.first_item
        url = self.url + "&page=%s" % page
        return OzonPageItem(
            await self.session.get_html_query_page(url)
        )


class OzonBrandSellerRangePricePageParser(OzonBrandSellerPageParser):

    def __init__(self, session, query, brand, seller, price):
        self.price = price
        super().__init__(session, query, brand, seller)

    async def initializate_url(self):
        url_encode = {
                "text": self.query, 
                "from_global": "true",
                "brand": self.brand_id,
                "seller": self.seller_id,
                "currency_price": f"{self.price-1};{self.price+1}",
                "deny_category_prediction": True,
            } 
        if self.brand_id is not None:
            url_encode["brand"] = self.brand_id
        if self.seller_id is not None:
            url_encode["seller"] = self.seller_id

        url = "https://www.ozon.ru/search/?%s" % urlencode(url_encode)
        self.first_item = OzonPageItem(
            await self.session.get_html_query_page(url + "&page=1")
        )

        url_encode['tf_state'] = self.first_item.tf_state
        self.url = "https://www.ozon.ru/search/?%s" % urlencode(url_encode)

        return self.first_item


    async def get_query_page(self, page):
        if page == 1:
            return self.first_item
        url = self.url + "&page=%s" % page
        return OzonPageItem(
            await self.session.get_html_query_page(url)
        )


class OzonBaseFindPlaceManager:
    """Базовый класс для нахождения места
    в выдаче 
    """
    ozon_page_parser_cls = OzonNotRedirectPageParser

    def __init__(self, session, query, need_find_nmid):
        self.session = session
        self.need_find_nmid = need_find_nmid
        self.query = query

        self._count = 0
        self._tasks = []
        self._run = True
        self._nmid_found = False
        self._place = None

    @property
    def place(self):
        return self._place

    @property
    def existence(self):
        return self._nmid_found

    @property
    def req_depth(self):
        return self.first_item.req_depth

    async def initializate_pages(self, pages):
        """Инициализация корутин"""
        self.page_parser = self.ozon_page_parser_cls(self.session, self.query)

        self.first_item = await self.page_parser.initializate_url()
        self.pages = pages

    async def _checker(self, page):
        """Проверяет каждую страницу на наличие товара"""
        if not self._nmid_found:
            if page != 1:
                page_item = await self.page_parser.get_query_page(page)
            else:
                page_item = self.first_item
            hrefs = page_item.links_query_page()
            nmid = int(self.need_find_nmid)
            self._count += len(hrefs)
            for count, href in enumerate(hrefs):
                if f"-{nmid}/" in href:
                    self._nmid_found = True
                    self._place = 36 * (page - 1) + count + 1
                if self._nmid_found:
                    break 

    async def start(self):
        req_depth = self.req_depth
        redirect_url = self.first_item.is_redirect_page()
        x = 0
        if req_depth > 0:
            for page in range(1, self.pages + 1):
                await self._checker(page)
                if self._count >= req_depth:
                    break


class OzonFindPlaceManagerForBrandAndSeller(OzonBaseFindPlaceManager):
    ozon_page_parser_cls = OzonBrandSellerPageParser

    def __init__(self, session, query, need_find_nmid, brand, seller):
        self.seller = seller
        self.brand = brand

        super().__init__(session, query, need_find_nmid)

    async def initializate_pages(self, pages):
        self.page_parser = self.ozon_page_parser_cls(
            self.session, self.query, self.brand, self.seller
        )
        
        self.first_item = await self.page_parser.initializate_url()
        self.pages = pages


class OzonFindPlaceManagerRedirect(OzonBaseFindPlaceManager):
    ozon_page_parser_cls = OzonRedirectPageParser

    @property
    def top_category(self):
        return self.first_item.top_category


class OzonFindPlaceManagerForBrandSellerAndRangePrice(OzonBaseFindPlaceManager):
    ozon_page_parser_cls = OzonBrandSellerRangePricePageParser

    def __init__(self, session, query, need_find_nmid, brand, seller, price):
        self.seller = seller
        self.brand = brand
        self.price = price

        super().__init__(session, query, need_find_nmid)

    async def initializate_pages(self, pages):
        self.page_parser = self.ozon_page_parser_cls(
            self.session, self.query, self.brand, self.seller, self.price
        )
        
        self.first_item = await self.page_parser.initializate_url()
        self.pages = pages


class OzonParser(BaseOzonParser):

    async def get_full_info_product(self, link_or_nmid):
        """Возвращает нужную информацию о товаре для индексации"""
        content = await self.get_full_info_from_api_product(link_or_nmid)
        return OzonProductItem(content)


class OzonIndexer:
    """Индексатор Озона"""
    def __init__(self, session, nmid):
        self.nmid = nmid
        self.session = session
        self.reader = csv.reader(
            open('ozon/ozon_parser/requests.csv', encoding='utf-8')
        )

    async def initializate_info(self):
        """Достаем всю нужную информацию из карточки товара"""
        self.product_item = await self.session.get_full_info_product(self.nmid)
        self.price = await self.session.get_price_product(self.nmid)

    def get_ready_data(self):
        """Инициализация чекера"""
        self.checker = Checker(self.nmid, self.product_item.split())
        self.resulted_queries = filter(self.checker.check_desc, self.reader)

    async def one_iterate(self, query):
        exception = None
        # Дается три попытки на выполнение одной итерации
        for i in range(2):
            try:
                keywords = query[0]
                frequency = query[1]
                need_data = await self.get_need_data(keywords)

                place = need_data['place'] 
                existence = need_data['existence']
                req_depth = need_data['req_depth']

                # если товар есть в поисковой выдаче, то собираем данные по рекламе, месту и топу выдачи
                if existence and req_depth != 0 and place is not None:
                    percent = (place / req_depth) * 100
                    spot_req_depth = str(round(percent, 2)).replace('.', ';')
                else:
                    spot_req_depth = None

                # возвращаем словарь со всеми значения
                result = {
                    'keywords': keywords,
                    'frequency': frequency,
                    'spot_req_depth': spot_req_depth,
                    **need_data,
                } 
                return result
            except Exception as e:
                #await asyncio.sleep(10)
                exception = traceback.format_exc()
                await asyncio.sleep(5)

        logger.error(f"Ошибка: {self.nmid}, {query[0]}")
        logger.error(exception)
        return f"Не удалось собрать данные по запросу '{query[0]}'"

    async def get_need_data(self, query):
        existence = None
        place = None
        req_depth = None
        priority_cat = None

        # Если товар был найден,
        # т.е не закончился и т.д

        if self.price is not None:
            brand_and_seller_manager = OzonFindPlaceManagerForBrandSellerAndRangePrice(
                self.session, 
                query, 
                self.nmid, 
                brand=self.product_item.brand_id,
                seller=self.product_item.seller_id,
                price=self.price
            )
            await brand_and_seller_manager.initializate_pages(10)
            await brand_and_seller_manager.start()

            existence = brand_and_seller_manager.existence
        else:
            existence = False

        if existence:
            find_place_manager = OzonFindPlaceManagerRedirect(self.session, query, self.nmid)
            await find_place_manager.initializate_pages(10)
            await find_place_manager.start()
            place = find_place_manager.place
            top_category = find_place_manager.top_category
            req_depth = find_place_manager.req_depth
        else:
            find_place_manager = OzonFindPlaceManagerRedirect(self.session, query, self.nmid)
            await find_place_manager.initializate_pages(1)
            await find_place_manager.start()
            top_category = find_place_manager.top_category
            req_depth = find_place_manager.req_depth


        return {
            "existence": existence,
            "priority_cat": top_category,
            "place": place,
            "req_depth": req_depth,
            #"top_category_req_depth": None
        }

    async def get_index_data(self):
        """Возвращает данные индексатора"""
        tasks = []
        results = []

        for i, query in enumerate(self.resulted_queries):
            #task = asyncio.create_task(self.one_iterate(query))
            #tasks.append(task)
            task = asyncio.create_task(self.one_iterate(query))
            tasks.append(task)

        #print("get_index_data")
        #results = await asyncio.gather(*tasks)
        #print(results)
        results = await asyncio.gather(*tasks)
        self.results = {
            'nmid': self.nmid,
            'brand': self.product_item.brand,
            'data': results,
        }

        return self.results


class OzonIndexerManager:

    def __init__(self, *nmids):
        self.nmids = nmids

    async def start_indexer(self, indexer):
        await indexer.initializate_info()
        indexer.get_ready_data()
        result = await indexer.get_index_data()
        return result

    async def run(self):
        #reader = csv.reader(
            #open('requests.csv', encoding='utf-8')
        #)
        async with OzonParser() as parser:
            # cоздает объекты индексаторы
            tasks = []

            for nmid in self.nmids:
                indexer = OzonIndexer(parser, nmid)
                task = asyncio.create_task(self.start_indexer(indexer))
                tasks.append(task)

            results = await asyncio.gather(*tasks)

            self.results = results


async def indexer_test():
    start = time.time()
    async with OzonParser() as parser:
        indexer = OzonIndexer(parser, 372612469)
        await indexer.initializate_info()
        indexer.get_ready_data()
        pprint(await indexer.get_index_data())
    end = time.time()
    print(end - start)

async def main():
    start = time.time()
    async with OzonParser() as parser:
        start = time.time()
        indexer = OzonIndexer(parser, 723486550)
        await indexer.initializate_info()
        indexer.get_ready_data()
        pprint(await indexer.get_index_data())

    print(time.time() - start)

async def test():
    start = time.time()
    # print(len(urls))
    manager = OzonIndexerManager(
        372608892,
        372612469,
        375043316,
        375048614,
        375084614,
        375086668,
        375090074,
        375102558,
        375126889,
        375130642,
        375384514,
        375416779,
        375428413,
        375431671,
        375446170,
        375483563,
        375494562,
        375503658,
        375515688,
        375530769,
        375531970,
        375820877,
        375852885,
        375855022,
        375860350,
        375873606,
        375878742,
        375885145,
        375887503,
        375907298,
        375919635,
        375920205,
        375950277,
        375960372,
        375967088,
        375971354,
        375976058,
        375976083,
        376016477,
        376035131,
        376041494,
        376046986,
        376055759,
        376057225,
        376057783,
        376061063,
        376063459,
        376066453,
        376071302,
        376074501,
        376074604,
        376076257,
        376085461,
        376091517,
        376095049,
        376095577,
        376096631,
        376099352,
        376107621,
        376107939,
        376111280,
        376115751,
        376118557,
        376123550,
        376127747,
        376128221,
        376132094,
        376136666,
        376153713,
        376208998,
        376226873,
        376236822,
        376238894,
        376244057,
        376251545,
        376256632,
        376257698,
        376258283,
        376258353,
        376750303,
        376769263,
        376779232,
        376787759,
        376807448,
        376812943,
        376818729,
        376829337,
        376829774,
        376832815,
        376837570,
        376841568,
        376843064,
        376852007,
        376878843,
        376881432,
        376887426,
        376889026,
        376939889,
        376956344,
        376979337,
        377014981,
        377018657,
        377023772,
        377039380,
        377044190,
        377047029,
        377050052,
        377058451,
        377061403,
        377078344,
        377127640,
        377129207,
        377142612,
        377145322,
        377149205,
        377155280,
        377162787,
        377166649,
        377167139,
        377167705,
        377168295,
        377173939,
        377174059,
        377178006,
        377180910,
        377181065,
        377182825,
        377183695,
        377184549,
        377186145,
        377187445,
        377187456,
        377189296,
        377190798,
        377190802,

    )
    await manager.run()
    pprint(manager.results)
    with open('results.pickle', 'wb') as file:
        pickle.dump(manager.results, file)

    logger.debug(time.time() - start)

async def test_base_find_place_manager():
    start = time.time()
    async with OzonParser() as parser:
        manager = OzonFindPlaceManagerForBrandAndSeller(
            parser, 
            "кубанский домовенок", 
            822239548, 
            brand = 87316948, 
            seller = 11070
        )
        await manager.initializate_pages(28)
        await manager.start()
        
        print(manager.existence)
        print(manager.place)
        print(manager.req_depth)
    #print(time.time() - start)

async def test_redirect():
    start = time.time()
    async with OzonParser() as parser:
        page_parser = OzonFindPlaceManagerRedirect(parser, "двери", 770470839)
        await page_parser.initializate_pages(28)
        await page_parser.start()
        print(page_parser.place)
        print(page_parser.existence)
        print(page_parser.top_category)

async def t():
    async with OzonParser() as parser:
        html = await parser.get_full_info_from_api_product(600941844)
        item = OzonProductItem(html)
        print(item.seller_id)
        print(item.brand_id)

async def get_json_product():
    async with OzonParser() as parser:
        content = parser.get("https://www.ozon.ru/api/entrypoint-api.bx/page/json/v2?url=/search/?text=%D1%81%D0%BF%D0%B8%D1%80%D0%B0%D0%BB%D0%B8%20%D0%BE%D1%82%20%D0%BA%D0%BE%D0%BC%D0%B0%D1%80%D0%BE%D0%B2")
        json = content.json()
        print(json)


if __name__ == "__main__":
    asyncio.run((test()))
