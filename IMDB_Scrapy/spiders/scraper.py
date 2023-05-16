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
    # storyline = scrapy.Field()
    # gross_us_canada = scrapy.Field()


class ImdbSpider(scrapy.Spider):
    name = 'IMDBSpider'
    allowed_domains = ['imdb.com']
    start_urls = ['https://www.imdb.com/chart/top/']
    user_agent = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
    ]
    custom_settings = {'FEED_FORMAT': 'csv', 'FEED_URI': 'IMDB.csv',
                       'FEED_EXPORT_ENCODING': 'utf-8',
                       'FEED_EXPORT_FIELDS': ['id', 'title', 'rating', 'volume', 'year', 'parental_guide', 'runtime_m',
                                              'genres',
                                              'director', 'writers',
                                              'stars', 'storyline', 'gross_us_canada', 'director_id', 'writers_id',
                                              'stars_id',
                                              ]
                       }

    def parse(self, response):
        for href in response.css("td.titleColumn a::attr(href)").getall():
            yield response.follow(url=href, callback=self.parse_movies)

    def parse_movies(self, response):
        item: ImdbItem = ImdbItem()

        # Movie's Id
        id_movie = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]//@href').get()
        item['id'] = id_movie.split('/')[2]

        # Movies
        item['title'] = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span/text()').get()

        item['year'] = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[1]/a/text()').get()

        item['parental_guide'] = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[2]/a/text()').get()

        # give time's format type is [h m] and change format to minutes
        time = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[3]/text()').get()
        h, m = time.split(' ')
        item['runtime'] = int(h.split('h')[0]) * 60 + int(m.split('m')[0])

        item['genres'] = ','.join(response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[1]/div[2]/a/span/text()').getall())

        director_list = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]/div/ul/li/a/text()').getall()
        id_director_list = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]/div/ul/li/a/@href').getall()

        temp = []
        for i, director in enumerate(director_list):
            id_director = id_director_list[i].split('/')[2]
            temp.append(f"{director_list[i]}|{id_director}")
        item['director'] = ','.join(temp)

        item['writers'] = ','.join(response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[2]/div/ul/li/a/text()').getall())

        item['stars'] = ','.join(response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[3]/div/ul/li/a/text()').getall())
        item['rating'] = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/span/div/div[2]/div[1]/span[1]/text()').get()
        volume = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/span/div/div[2]/div[3]/text()').get()
        if volume[-1] == 'M':
            item['volume'] = int(float(volume.split("M"))*1000000)
        else:
            item['volume'] = int(float(volume.split("K")) * 1000)
        # item['storyline'] = response.xpath(
        #     '//*[@id="__next"]/main/div/section[1]/div/section/div/div[1]/section[6]/div[2]/div[1]/div/div/text()').get()
        #
        # item['gross_us_canada'] = response.xpath(
        #     '//*[@id="__next"]/main/div/section[1]/div/section/div/div[1]/section[13]/div[2]/ul/li[2]/div/ul/li/span/text()').get()

        return item
