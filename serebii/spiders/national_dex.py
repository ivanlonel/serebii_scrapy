import scrapy


class NationalDexSpider(scrapy.Spider):
    name = 'national_dex'
    allowed_domains = ['www.serebii.net']
    start_urls = ['https://www.serebii.net/pokemon/all.shtml']

    def parse(self, response):
        for pokemon in response.xpath('//table[@class="dextable"]/tr/td[@class="fooinfo"][3]/a'):
            yield response.follow(url=pokemon.xpath(".//@href").get(), callback=self.parse_pokemon)
            #yield pokemon.xpath(".//text()").get()

    def parse_pokemon(self, response):
#        meta = {
#            'name': response.xpath('//aside[@id="rbar"]/table[@class="tooltab"][1]/tr[2]/td[1]/text()').get()
#        }

        return response.follow(url=response.xpath('//div[@id="content"]/main/table[contains(.//tr/td/p/font/b/u, "Game Databases")]//tr/td/div/div[1]/a/@href').get(),
                               callback=self.parse_by_gen,
                               #meta=meta
                              )

    def parse_by_gen(self, response):
        #Charizard Gen7:
        #//div[@id="moves"]/ul/li[starts-with(@title, "S")]/a[@name = "stats"]/following-sibling::table[@class="dextable"][1]//tr[2]/td[@class="fooevo"]/text()
        #Deoxys Gen7
        #//div[@id="content"]/main/div/div/a[@name="stats"]/following-sibling::table[@class="dextable"][1]//tr[2]/td[@class="fooevo"]/text()
        #Charizard Gen8:
        #//div[@id="content"]/main/div[2]/a[@name = "stats"]/following-sibling::table[@class="dextable"][1]//tr[2]/td[@class="fooevo"]/text()
        #Zacian/Zamazenta:
        #//div[@id="content"]/main/div[2]/p[child::a[@name="stats"]]/following-sibling::table[@class="dextable"][1]//tr[2]/td[@class="fooevo"]/text()

        #(//div[@id="moves"]/ul/li[starts-with(@title, "S")] | //div[@id="content"]/main/div/div | //div[@id="content"]/main/div[2])/*[self::p/a[@name="stats"] or self::a[@name="stats"]]/following-sibling::table[@class="dextable"][1]//tr[2]/td[@class="fooevo"]/text()

        #Types:

        #Charizard Gen7:
        #//div[@id="content"]/main/div/div/*[self::p[child::a[@name='general']] or self::a[@name='general']]/following-sibling::table[@class='dextable'][2]//tr/td[@class='cen']/a/img[@class='typeimg']/@alt
        #Charizard Gen8:
        #//div[@id="content"]/main/div[2]/*[self::p[child::a[@name='general']] or self::a[@name='general']]/following-sibling::table[@class='dextable'][2]//tr/td[@class='cen']/a/img[@class='typeimg']/@alt

        #Charizard (Gen7/8), Deoxys, Kyurem (Gen7/8)
        #   Does not work for Rotom (Gen7/8), Zacian, Urshifu etc:
        #(//div[@id="content"]/main/div/div | //div[@id="content"]/main/div[2])/*[self::p[child::a[@name="general"]] or self::a[@name="general"]]/following-sibling::table[@class="dextable"][2]//tr/td[@class="cen"]/a/img[@class="typeimg"]/@alt

        #(//div[@id="content"]/main/div/div | //div[@id="content"]/main/div[2])/*[self::p[child::a[@name="general"]] or self::a[@name="general"]]/following-sibling::table[@class="dextable"][2]//tr[2]/td[@class="cen"]//a[parent::td[@class="cen" or parent::tr[not(preceding-sibling::tr)]]]/img[@class="typeimg"]/@alt


        #Abilities:

        #(//div[@id="content"]/main/div/div | //div[@id="content"]/main/div[2])/*[self::p[child::a[@name="general"]] or self::a[@name="general"]]/following-sibling::table[@class="dextable"][3]//tr/td/a[not(preceding-sibling::b)]/b/text()


        #Number:
        #(//div[@id="content"]/main/div/div | //div[@id="content"]/main/div[2])/*[self::p[child::a[@name="general"]] or self::a[@name="general"]]/following-sibling::table[@class="dextable"][2]//tr/td[@class='fooinfo']/table//tr[child::td[1][child::b[text()='National']]]/td[2]/text()

        general_info = response.xpath('(//div[@id="content"]/main/div/div | //div[@id="content"]/main/div[2])/*[self::p[child::a[@name="general"]] or self::a[@name="general"]]')

        national_dex_id = general_info.xpath('./following-sibling::table[@class="dextable"][2]//tr/td[@class="fooinfo"]/table//tr[child::td[1][child::b[text()="National"]]]/td[2]/text()').get()

        name = general_info.xpath('./following-sibling::table[@class="dextable"][2]//tr[2]/td[@class="fooinfo"][1]/text()').get()

        types_td = general_info.xpath('./following-sibling::table[@class="dextable"][2]//tr[2]/td[@class="cen"]')
        types = types_td.xpath('.//a[parent::td[@class="cen" or parent::tr[not(preceding-sibling::tr)]]]/img/@alt').getall()  # not sure why parent::tr[not(preceding-sibling::tr)] works and parent::tr[1] doesn't.

        abilities_td = general_info.xpath('./following-sibling::table[@class="dextable"][3]//tr[2]/td[@class="fooinfo"]')
        common_abilities = abilities_td.xpath('./a[not(preceding-sibling::b)]/b/text()').getall()  # I hate you, Basculin
        hidden_ability = abilities_td.xpath('./b[text()="Hidden Ability"][1]/following-sibling::a[1]/b/text()').get()

        stats_table = response.xpath('(//div[@id="moves"]/ul/li[starts-with(@title, "S")] | //div[@id="content"]/main/div/div | //div[@id="content"]/main/div[2])/*[self::p/a[@name="stats"] or self::a[@name="stats"]]/following-sibling::table[@class="dextable"][1]')
        stats_keys = stats_table.xpath('.//tr[2]/td[@class="fooevo"]/text()').getall()
        stats_vals = stats_table.xpath('.//tr[3]/td[@class="fooinfo" and position()>1]/text()').getall()

        return {
            'id': int(national_dex_id[1:]),
            'name': name,
            'types': [t.replace('-type','') for t in types],
            'abilities': {
                'common': common_abilities,
                'hidden': hidden_ability
            },
            'stats': dict(zip(stats_keys, map(int, stats_vals)))
        }