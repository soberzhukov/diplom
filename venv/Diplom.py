import requests
from pprint import pprint
import os
from json import dump
import logging

logging.basicConfig(filename='info.log',
                    level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s"
                    )

class VkUser:
    URL = 'https://api.vk.com/method/'
    def __init__(self, token, version):
        self.token = token
        self.version = version
        self.params = {
            'access_token': self.token,
            'v': self.version
        }
        self.owner_id = requests.get(self.URL + 'users.get', self.params).json()['response'][0]['id'] # Получение id


    def download(self, id, albom, quantity):
        photos_list = self._take_photos_list(id, albom, quantity)
        self._writing_to_json(photos_list)
        logging.debug('Записали информацию по фотографиям в info.json')
        number = 0
        os.mkdir('Photos_vk')
        for photo in photos_list:
            url_photo = photo['url_photo']
            name_photo = photo['name_photo']
            resp = requests.get(url_photo)
            resp.raise_for_status()
            with open(os.path.join('Photos_vk', name_photo), 'wb') as f:
                f.write(resp.content)
                number += 1
                logging.debug(f'Загрузили фотографию {number} в директорию Photos_vk')


    def _take_photos_list(self, id, albom, quantity):
        """
            возвращает список словарей [{name_photo: name, size_photo: size, url_photo:url}]
        """
        photos_list = list()
        metod = 'photos.get'
        params = {
            **self.params,
            'owner_id': id,
            'album_id': albom,
            'extended': 1, # доп параметры лайки
        }
        resp = requests.get(self.URL + metod, params=params)
        resp.raise_for_status()
        photos = resp.json()['response']['items']
        count_likes_in_list = dict()
        for photo in photos:
            count_likes_in_list[photo['likes']['count']] = count_likes_in_list.get(photo['likes']['count'], 0) + 1
        for photo in photos:
            if count_likes_in_list[photo['likes']['count']] == 1:
                photos_list.append({
                    'name_photo': f"{photo['likes']['count']}.jpg",
                    'size_photo': photo['sizes'][-1]['type'],
                    'url_photo': photo['sizes'][-1]['url']
                })
            else:
                photos_list.append({
                    'name_photo': f"{photo['likes']['count']}_{photo['date']}.jpg",
                    'size_photo': photo['sizes'][-1]['type'],
                    'url_photo': photo['sizes'][-1]['url']
                })
        return photos_list[:quantity]


    def _writing_to_json(self, photos_list):
        """
            запись в json файл
        """
        list_json = list()
        for photo in photos_list:
            list_json.append({
                "file_name": photo['name_photo'],
                "size": photo['size_photo']
            })
        with open(os.path.join('info.json'), 'w') as f:
            dump(list_json, f, indent=1)



class YandexDisk:
    URL = 'https://cloud-api.yandex.net/v1/disk/resources/'
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': f'OAuth {self.token}'
        }


    def dow(self, directory_name):
        number = 0
        params = {
            'path': f'disk:/{directory_name}'
        }
        resp = requests.put(
            url = self.URL,
            params=params,
            headers=self.headers
        )
        resp.raise_for_status()
        for file_name in os.listdir(path="Photos_vk"):
            params = {
                'path': f'disk:/{directory_name}/{file_name}'
            }
            resp_1 = requests.get(
                url = self.URL + 'upload',
                params = params,
                headers = self.headers
            )
            resp_1.raise_for_status()
            with open(os.path.join('Photos_vk', file_name), 'rb') as f:
                resp_2 = requests.post(resp_1.json()['href'], files={'file':f})
                number += 1
                logging.debug(f'Загрузили фотографию {number} на Яндекс диск')






if __name__ == '__main__':
    token_vk = token
    user_vk1 = VkUser(token_vk, 5.126)
    user_vk1.download(ID, 'profile', 2)

    token_yandex = token
    user_yandex1 = YandexDisk(token_yandex)
    user_yandex1.dow('photos_vk')
