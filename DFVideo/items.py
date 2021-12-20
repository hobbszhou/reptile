# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# class DfvideoItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass


class PostItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    table_name = 'posts'
    created_at = scrapy.Field()
    video = scrapy.Field()
    pic = scrapy.Field()
    pid = scrapy.Field()
    title = scrapy.Field()
    category = scrapy.Field()
    play_counts = scrapy.Field()
    like_counts = scrapy.Field()
    description = scrapy.Field()


# 作者的信息
class ComposerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    table_name = 'composers'
    article = scrapy.Field()
    liker = scrapy.Field()
    fans = scrapy.Field()
    follower = scrapy.Field()
    area = scrapy.Field()


# 评论
class CommentItem(scrapy.Item):
    table_name = 'comments'
    username = scrapy.Field()
    content = scrapy.Field()

