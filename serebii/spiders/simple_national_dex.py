import scrapy


class SimpleNationalDexSpider(scrapy.Spider):
    name = 'simple_national_dex'
    allowed_domains = ['www.serebii.net']
    start_urls = ['https://www.serebii.net/pokemon/all.shtml']

    def parse(self, response):
        stats_keys = ["HP", "Attack", "Defense", "Sp. Attack", "Sp. Defense", "Speed"]

        for pokemon in response.xpath('//table[@class="dextable"]/tr[position()>2]'):
            abilities = pokemon.xpath('./td[5]/a/text()').getall()

            yield {
                'id': int(pokemon.xpath('normalize-space(./td[1]/text())').get()[1:]),
                'name': pokemon.xpath('./td[3]/a/text()').get(),
                'types': [tp.split('/')[-1].capitalize() for tp in pokemon.xpath('./td[4]/a/@href').getall()],
                'abilities': {
                    'common': [abilities[0]] if len(abilities) < 3 else abilities[:-1],
                    'hidden': abilities[-1] if len(abilities) > 1 else None
                },
                'stats': dict(zip(stats_keys, map(int, pokemon.xpath('./td[position() > 5]/text()').getall())))
            }
