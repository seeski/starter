import asyncio

from django.test import TestCase
from .ozon_parser import OzonIndexerManager, OzonFindPlaceManagerRedirect, OzonParser

class TestOzonParser(TestCase):

	def test_check_manager(self):
		manager = OzonIndexerManager(
			946781813
		)
		asyncio.run(manager.run())


async def test():
	pass