# from requests.api import request
import scrapy
import re
from scrapy import Request
import string
import json
from DFVideo.items import PostItem, ComposerItem,CommentItem 
from os import path
import os
import requests
from contextlib import closing
def strip(s):
    if s:
        return s.strip()
    return ''


class PashipinSpider(scrapy.Spider):
    name = 'paShiPin'
    allowed_domains = ['xinpianchang.com']
    start_urls = ['https://www.xinpianchang.com/channel/index/sort-like?from=tabArticle']
    def parse(self, response):
        url="https://www.xinpianchang.com/a{}?from=ArticleList"
        pid_list = response.xpath('//div[@class="channel-con"]//ul[@class="video-list"]//li[@class="enter-filmplay"]/@data-articleid').extract()

        for pid in pid_list:

            urltmp = url.format(pid)


            request = response.follow(urltmp, self.parse_post)
            request.meta['pid'] = pid
            yield request 

        # 获取下方的1,2,3,4,5,6页 //div[@class="page"]//a//@href
        pageLists = response.xpath('//div[@class="page"]//a//@href').extract()
        pageUrlPrefix = 'https://www.xinpianchang.com'
        for page in pageLists:
            pageUrl=pageUrlPrefix+page

            return
            request = response.follow(pageUrl, self.parse_post)
            yield request 
    def parse_post(self, response):
        pid = response.meta['pid']
        post = {
            'pid': pid
        }
        title = response.xpath('/html/body/div[8]/div[2]/div[1]/div[1]/div[1]/div[2]/h3/text()').get()

        post['title'] = response.xpath('/html/body/div[8]/div[2]/div[1]/div[1]/div[1]/div[2]/h3/text()').get()
        url = "https://mod-api.xinpianchang.com/mod/api/v2/media/{}?appKey=61a2f329348b3bf77&extend=userInfo%2CuserStatus"

        vid, = re.findall('var vid = \"(\w+)\"\;', response.text)
        video_url = url.format(vid)
        cates = response.xpath('//span[contains(@class, "cate")]//text()').extract()
        cates2 = ''.join([cate.strip() for cate in cates])
        # print(cates2)
        post['category']=cates2
        created = response.xpath('//div//ul[@class="creator-list"]//span[contains(@class,"name")]//text()').extract()

        created2 =','.join([cate.strip() for cate in created])

        post['created_at']=created2
        post['play_counts']=response.xpath('//div[@class="filmplay-container"]//div[@class="filmplay-data"]//div//i/@data-curplaycounts').extract()[0]
        post['like_counts']=response.xpath('//span[@class="pick-wrap like"]//span//@data-counts').extract()[0]
        desc=response.xpath('//p[contains(@class, "desc")]//text()').extract()
        desc2=''.join([strip(cate) for cate in desc])
        post['description']=desc2
        request = Request(video_url, callback=self.parse_video)
        request.meta['post'] = post
        yield request

        comt_url="https://app2.xinpianchang.com/comments?resource_id={}&type=article&page=1&per_page=24"
        comt_url2=comt_url.format(pid)
        request = Request(comt_url2, callback=self.parse_comment)
        request.meta['pid'] = pid
        yield request

        # 爬取创作者的详情的跳转链接 //div[@class="creator-info"]//a/@href
        urlPrefix="https://www.xinpianchang.com"
        creatorUrlLists=response.xpath('//div[@class="creator-info"]//a/@href').extract()
        for elem in creatorUrlLists:
            curUrl=urlPrefix+elem
            request = response.follow(curUrl, self.parse_creator)
            request.meta['pid'] = pid
            yield request



    def parse_video(self, response):
        post2 = PostItem()
        post = response.meta['post']
        result = json.loads(response.text)

        post2['video'] = result['data']['resource']['progressive'][0]['url']
        post2['pic'] = str(result['data']['cover'])
        post2['pid'] = str(post['pid'])
        post2['title'] =  str(post['title'])
        post2['category'] =  str(post['category'])
        post2['created_at'] = str(post['created_at'])
        post2['like_counts'] = str(post['like_counts'])
        post2['description'] = str(post['description'])
        post2['play_counts'] =  str(post['play_counts']) 

        base_dir =  path.join(path.curdir, 'VideoDownload')
        # videoName = post2['title']+'.mp4'
        file_name = path.join(path.curdir, 'VideoDownload')+ '\\' + post2['title']+'.mp4'
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        print("file_name-----------", file_name, ' ========= ', base_dir)
        # down2 = requests.get().get(post2['video'], stream=True).content
        # with open(file_name, 'wb') as f:
        #     f.write(down2)

        # # 下载视频方案一：
        # with requests.get(post2['video'], stream=True) as r:
        #     chunk_size = 1024
        #     # content_size = int(r.headers['content-length'])
        #     print('开始下载')
        #     with open(file_name, "wb") as f:
        #         for chunk in r.iter_content(chunk_size=chunk_size):
        #             f.write(chunk)
        # # 下载视频方案二： 增加closing 避免内存泄露
        # with closing(requests.get(post2['video'], stream=True)) as r:
        #     chunk_size = 1024
        #     # content_size = int(r.headers['content-length'])
        #     print('开始下载')
        #     with open(file_name, "wb") as f:
        #         for chunk in r.iter_content(chunk_size=chunk_size):
        #             f.write(chunk)

        # 将下好的即使存入硬盘，方案三: 程序正常运行了，不过我盯着这文件，怎么大小不见变啊，到底是完成了多少了呢？还是要让下好的内容及时存进硬盘，还能省点内存是不是
        # with closing(requests.get(post2['video'], stream=True)) as r:
        #     chunk_size = 1024
        #     content_size = int(r.headers['content-length'])
        #     print('下载开始')
        #     with open(file_name, "wb") as f:
        #         for chunk in r.iter_content(chunk_size=chunk_size):
        #             f.write(chunk)
        #             f.flush()
        #             os.fsync(f.fileno())

        # 方案4，增加进度条:文件以肉眼可见的速度在增大，真心疼我的硬盘，还是最后一次写入硬盘吧，程序中记个数就好了：
        with closing(requests.get(post2['video'], stream=True)) as r:
            chunk_size = 1024
            content_size = int(r.headers['content-length'])
            print('下载开始')
            with open(file_name, "wb") as f:
                n = 1
                for chunk in r.iter_content(chunk_size=chunk_size):
                    loaded = n*1024.0/content_size
                    f.write(chunk)
                    print('视频名字:', post2['title'],  ' 已下载{0:%}'.format(loaded))
                    n += 1

        yield post2


    def parse_comment(self, response):

        comment = CommentItem()
        result = json.loads(response.text)
        # commentAll = {}
        contentLists = []
        contents = result["data"]["list"]
        idx = 0
        while idx < len(contents):
            comment['content'] = contents[idx]["content"]
            comment['username'] = contents[idx]["userInfo"]["username"]
            contentLists.insert(idx, comment)
            idx += 1
            yield comment

        next_page = result['data']['next_page_url']
        if next_page:
            next_page = "https://app2.xinpianchang.com" + next_page
            # print("-------next_page====", next_page)
            yield response.follow(next_page, self.parse_comment)

    def parse_creator(self, response):
        composer = ComposerItem()
        # 拿到作品名称， 进行遍历 //ul[@class="article-list"]//p[@class="fs_14 fw_600 c_b_3 line-hide-1"]//text()
        aticleNameLists = response.xpath('//ul[@class="article-list"]//p[@class="fs_14 fw_600 c_b_3 line-hide-1"]//text()').extract()

        article = '          |           '.join([cate.strip() for cate in aticleNameLists])

        composer['article'] = article


        #2 人气 //div[@class="creator-info-wrap"]//span[contains(@class, "like-counts")]//text()
        composer['liker'] = response.xpath('//div[@class="creator-info-wrap"]//span[contains(@class, "like-counts")]//text()').extract()[0]

        # 3 粉丝  //span[contains(@class,"fans-counts")]//text()
        composer['fans'] = response.xpath('//span[contains(@class,"fans-counts")]//text()').extract()[0]
        # 4 关注 follower //span[@class="follow-wrap"]//span[contains(@class,"fw_600")]//text()
        composer['follower'] = response.xpath('//span[@class="follow-wrap"]//span[contains(@class,"fw_600")]//text()').extract()[0]
        # 地址 /html/body/div[8]/div[3]/div/p[3]/span[5]/text()
        composer['area'] = response.xpath('/html/body/div[8]/div[3]/div/p[3]/span[5]/text()').extract()[0]

        yield composer
