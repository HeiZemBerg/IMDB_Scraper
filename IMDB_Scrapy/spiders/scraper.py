import scrapy


class ImdbItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    parental_guide = scrapy.Field()
    year = scrapy.Field()
    runtime = scrapy.Field()
    genres = scrapy.Field()
    director = scrapy.Field()
    writers = scrapy.Field()
    stars = scrapy.Field()
    rating = scrapy.Field()
    volume = scrapy.Field()


class ImdbSpider(scrapy.Spider):
    name = 'IMDBSpider'
    allowed_domains = ['imdb.com']
    start_urls = ['https://www.imdb.com/chart/top/']
    user_agent = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
    ]
    custom_settings = {'FEED_FORMAT': 'csv', 'FEED_URI': 'IMDB.csv',
                       'FEED_EXPORT_ENCODING': 'utf-8',
                       'FEED_EXPORT_FIELDS': ['id', 'title', 'rating', 'volume', 'year', 'parental_guide', 'runtime',
                                              'genres',
                                              'director', 'writers',
                                              'stars'
                                              ]
                       }

    def parse(self, response):
        for href in response.css("td.titleColumn a::attr(href)").getall():
            yield response.follow(url=href, callback=self.parse_movies)

    def parse_movies(self, response):
        item: ImdbItem = ImdbItem()

        # Movie's Id
        id_movie = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]//@href').extract()
        item['id'] = id_movie[-1].split('/')[2]

        # Movies
        item['title'] = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span/text()').extract()
        # Year
        item['year'] = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[1]/a/text()').extract()

        item['parental_guide'] = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[2]/a/text()').extract()

        # give time's format type is [h m]
        item['runtime'] = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[3]/text()').extract()

        # Movie's Genres
        item['genres'] = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[1]/div[2]/a/span/text()').extract()

        # Director
        director_list = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]/div/ul/li/a/text()').extract()
        id_director_list = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]/div/ul/li/a/@href').extract()

        temp = []
        for i, director in enumerate(director_list):
            id_director = id_director_list[i].split('/')[2]
            temp.append(f"{director_list[i]}|{id_director}")
        item['director'] = ','.join(temp)

        # Writers
        item['writers'] = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[2]/div/ul/li/a/text()').extract()

        # Stars
        item['stars'] = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[3]/div/ul/li/a/text()').extract()

        # Rating
        item['rating'] = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/span/div/div[2]/div[1]/span[1]/text()').extract()

        # Volume
        volume = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/span/div/div[2]/div[3]/text()').extract()
        if volume[-1][-1] == 'M':
            item['volume'] = int(float(volume[-1].split("M")[0]) * 1000000)
        else:
            item['volume'] = int(float(volume[-1].split("K")[0]) * 1000)

        return item
