from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Optional

import requests
from pydantic import BaseModel, ValidationError

import _env as env

API_URL = f'{env.BASE_URL}/wp-json/wp/v2'

DRY_RUN = os.getenv('WPAC_MODE', '') != 'dangerous'


class Render(BaseModel):
    rendered: str


class MediaDetails(BaseModel):
    filesize: int
    sizes: dict[str, Any]
    width: Optional[int] = None
    height: Optional[int] = None


class Link(BaseModel):
    href: str
    targetHints: Optional[dict[str, Any]]
    embeddable: bool = False


class Links(BaseModel):
    self: list[Link]
    collection: list[Link]
    about: list[Link]
    author: list[Link]
    replies: list[Link]


class MediaItem(BaseModel):
    _links: Links
    id: int
    date: datetime
    date_gmt: datetime
    guid: Render
    modified: datetime
    modified_gmt: datetime
    slug: str
    status: str
    type: str
    link: str
    title: Render
    author: int
    featured_media: int
    comment_status: str
    ping_status: str
    template: str
    meta: list[dict[str, Any]]
    class_list: list[str]
    description: Render
    caption: Render
    alt_text: str
    mime_type: str
    media_details: MediaDetails
    post: Optional[int]
    source_url: str

    def is_orphan(self):
        return self.post is None

    def delete(self):
        if DRY_RUN:
            logging.info(f'[DRY RUN] deleting {self.id} {self.slug}')
        else:
            logging.info(f'deleting {self.id} {self.slug}')
            res = requests.delete(
                f'{API_URL}/media/{self.id}',
                auth=(env.USERNAME, env.PASSWORD),
                params={'force': 'true'}
            )
            print(res.status_code, res.text)


class MediaItems(BaseModel):
    items: list[MediaItem]

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, slice):
        return self.items[slice]

    def filter(self, predicate):
        return MediaItems(items=[x for x in self.items if predicate(x)])

    def map(self, func):
        return [func(x) for x in self.items]

    def extend(self, other: MediaItems):
        self.items.extend(other.items)

    def limit(self, count):
        return MediaItems(items=self[:count])

    def delete(self):
        logging.info(f'Deleting {len(self)} items')
        for item in self:
            item.delete()


def _load_media(page):
    res = requests.get(
        f'{API_URL}/media',
        params={
            'per_page': 100,
            'page': page,
        },
    )
    return f'{{ "items": {res.text} }}'


def load_media() -> MediaItems:
    items = MediaItems(items=[])
    page = 1
    while True:
        data = _load_media(page)
        try:
            items.extend(MediaItems.model_validate_json(data))
        except ValidationError as e:
            break
        page += 1
        if page > 20:
            break
    return items


def main():
    logging.basicConfig(
        filename='attachment_cleaner.log',
        level=logging.INFO,
        format='[%(asctime)s - %(levelname)s] %(message)s'
    )

    threshold = datetime.now() - timedelta(days=28)
    items = load_media()
    dead_items = (items
        .filter(MediaItem.is_orphan)
        .filter(lambda item: item.date < threshold)
        .filter(lambda item: item.mime_type == "application/pdf")
        .filter(lambda item: 'pew-news' in item.slug or 'priory-diary' in item.slug or 'service-list' in item.slug)
    )
    dead_items.delete()


if __name__ == '__main__':
    exit(main())

