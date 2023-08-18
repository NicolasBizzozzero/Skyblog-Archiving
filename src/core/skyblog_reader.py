import os
import re
import shutil

from tinycss import CSS21Parser
import requests
from bs4 import BeautifulSoup, ResultSet

from logger import logger

from core.utils import request_page

from core.post import Post


class SkyblogReader:
    def __init__(self, username: str):
        self.username = username
        self.max_page_number = None
        self.articles = None
        self.title = None
        self.description = None
        self.url_profile_picture = None
        self.url_background = None
        self.color_background = None
        self.color_theme = None
        self.color_block_title = None
        self.color_text_title = None
        self.color_articles_background = None

    def get(self):
        # Request first page once and parse it
        html_first_page = request_page(self.username, page_number=1)
        html_content = BeautifulSoup(html_first_page, "html.parser")

        # Get the highest page number
        self.max_page_number = self.get_highest_page_number(html_content)
        logger.debug(f"Number of pages: {self.max_page_number}")

        # Fetch all blog articles
        self.articles = self.get_articles()
        logger.debug(f"Retrieved {len(self.articles)} article(s)")

        # Get the profile title
        self.title = self.get_title(html_content)
        logger.debug(f"Blog title: {self.title}")

        # Get the profile description
        self.description = self.get_description(html_content)

        # Get the mini-profile picture
        self.url_profile_picture = self.get_url_profile_picture(
            soup=html_content, username=self.username
        )
        logger.debug(f"Profile picture URL: {self.url_profile_picture}")

        # Get the background picture URL
        self.url_background = self.get_background_picture_url(html_content)
        logger.debug(f"Background picture URL: {self.url_background}")

        # Get the background color
        self.color_background = self.get_color_background(html_content)
        logger.debug(f"Background color: #{self.color_background}")

        # Get the theme color
        self.color_theme = self.get_color_theme(html_content)
        logger.debug(f"Theme color: #{self.color_theme}")

        # Get the color of the title block
        self.color_block_title = self.get_color_block_title(html_content)
        logger.debug(f"Color of the block title: #{self.color_block_title}")

        # Get the color of the title block
        self.color_text_title = self.get_color_text_title(html_content)
        logger.debug(f"Color of the text title: #{self.color_text_title}")

        # Get the color of the articles block
        self.color_articles_background = self.get_color_articles_background(
            html_content
        )
        logger.debug(
            f"Color of the articles background: #{self.color_articles_background}"
        )

    def get_articles(self):
        # We expect to have at most self.pages * 5 posts to load
        # Loop from 1.html until max_pages_number
        posts = []
        for i in range(1, self.max_page_number + 1):
            html_content = request_page(self.username, page_number=i)
            soup = BeautifulSoup(html_content, "html.parser")
            posts += _html_to_post(soup)
        return posts

    @staticmethod
    def get_title(soup: BeautifulSoup) -> str:
        title = soup.find("h1", class_="blogtitle")
        if title is not None:
            return title.text.strip()
        return ""

    @staticmethod
    def get_description(soup: BeautifulSoup) -> str:
        description = soup.find("p", class_="description")
        return description.__repr__()

    @staticmethod
    def get_url_profile_picture(soup: BeautifulSoup, username: str) -> str:
        logger.debug(f'Requesting URL "https://{username}.skyrock.com/photo.html"')
        response = requests.get(f"https://{username}.skyrock.com/photo.html")

        picture_soup = BeautifulSoup(response.text, "html.parser")
        url_picture = picture_soup.find("img", id="laphoto")["src"]
        if not url_picture:
            # No profile picture found, fallback to skyblog avatar
            url_picture = soup.find("img", class_="avatar")["src"]

        return url_picture

    @staticmethod
    def get_highest_page_number(soup: BeautifulSoup) -> int:
        pagination = soup.find("ul", class_="pagination")
        if pagination is None:
            # No pagination found, thus there is only one page (<= 5 posts)
            return 1
        all_pages = pagination.find_all("li")
        max_page = all_pages[-2].get_text().replace(".", "").strip()
        return int(max_page)

    @staticmethod
    def get_color_block_title(soup: BeautifulSoup) -> str:
        color = "000000"  # Default color, black

        # There is either a pasted CSS content in a style tag called "template_css_perso", or a file in a
        # link called "template_css"
        style = soup.find("style", id="template_css_perso")
        if style:
            style = str(style.contents[0]).split("\n")[1]
            style = CSS21Parser().parse_stylesheet(style)
            for rule in style.rules:
                if ".bloc_title" in str(rule):
                    for declaration in rule.declarations:
                        if " color:" in str(declaration):
                            color = str(declaration.value[0].value)
                            break
        else:
            # Fetch CSS file
            url_css = soup.find("link", id="template_css")["href"]
            style = CSS21Parser().parse_stylesheet(requests.get(url_css).text)
            for rule in style.rules:
                if ".bloc_title" in str(rule) and " background:" in str(
                    rule.declarations
                ):
                    color = rule.declarations[0].value[0].value[1:]
                    break

        if color[0] == "#":
            color = color[1:]
        return color

    @staticmethod
    def get_color_text_title(soup: BeautifulSoup) -> str:
        color = "fff"  # Default color, white

        # There is either a pasted CSS content in a style tag called "template_css_perso", or a file in a
        # link called "template_css"
        style = soup.find("style", id="template_css_perso")
        if style:
            style = str(style.contents[0])
            color = re.findall(r"#linkPopup\{color:#([a-fA-F0-9]{3,6})", style)
            if not color:
                # No posts, blog is empty
                return ""
            color = color[0]
        else:
            # Fetch CSS file
            url_css = soup.find("link", id="template_css")["href"]
            style = CSS21Parser().parse_stylesheet(requests.get(url_css).text)
            for rule in style.rules:
                if ".bloc_title" in str(rule) and " color:" in str(rule.declarations):
                    color = rule.declarations[0].value[0].value[1:]
                    break
        return color

    @staticmethod
    def get_color_articles_background(soup: BeautifulSoup) -> str:
        color = "ffffff"  # Default color, white

        # There is either a pasted CSS content in a style tag called "template_css_perso", or a file in a
        # link called "template_css"
        style = soup.find("style", id="template_css_perso")
        if style:
            style = str(style.contents[0])
            color = re.findall(
                r"#promos_ads\{color:#[a-fA-F0-9]{3,6};background-color:#([a-fA-F0-9]{3,6})",
                style,
            )
            if not color:
                # No posts, blog is empty
                return ""
            color = color[0]
        else:
            # Fetch CSS file
            url_css = soup.find("link", id="template_css")["href"]
            style = CSS21Parser().parse_stylesheet(requests.get(url_css).text)
            for rule in style.rules:
                if ".bloc," in str(rule) and "background" in str(rule.declarations):
                    color = rule.declarations[0].value[0].value[1:]
                    break
        return color

    @staticmethod
    def get_background_picture_url(soup: BeautifulSoup) -> str | None:
        style = soup.find("body")
        if not style.get("style"):
            # No background picture found
            return None

        # Retrieve the URL from the CSS
        url = re.search(r"(https?://[^\s]+)", style["style"])[0]
        url = url[:-2]  # Remove ");" at the end of the url
        return url

    @staticmethod
    def get_color_background(soup: BeautifulSoup) -> str | None:
        color = "ffffff"  # Default color, white

        # There is either a pasted CSS content in a style tag called "template_css_perso", or a file in a
        # link called "template_css"
        style = soup.find("style", id="template_css_perso")
        if style:
            style = str(style.contents[0])
            color = re.findall(
                r"body\{background-color:#([a-fA-F0-9]{3,6})",
                style,
            )
            if not color:
                # No posts, blog is empty
                return ""
            color = color[0]
        else:
            # Fetch CSS file
            url_css = soup.find("link", id="template_css")["href"]
            style = CSS21Parser().parse_stylesheet(requests.get(url_css).text)
            for rule in style.rules:
                if ".consult," in str(rule) and " background:" in str(
                    rule.declarations
                ):
                    color = rule.declarations[0].value[0].value[1:]
                    break
        return color

    @staticmethod
    def get_color_theme(soup: BeautifulSoup) -> str | None:
        color = "000000"  # Default color, black

        # There is either a pasted CSS content in a style tag called "template_css_perso", or a file in a
        # link called "template_css"
        style = soup.find("style", id="template_css_perso")
        if style:
            style = str(style.contents[0]).split("\n")[1]
            style = CSS21Parser().parse_stylesheet(style)
            for rule in style.rules:
                if ".bloc-description" in str(rule):
                    for declaration in rule.declarations:
                        if "background-color" in str(declaration):
                            color = str(declaration.value[0].value)
                            break
                    break
        else:
            # Fetch CSS file
            url_css = soup.find("link", id="template_css")["href"]
            style = CSS21Parser().parse_stylesheet(requests.get(url_css).text)
            for rule in style.rules:
                if ".bloc-description" in str(rule) and " background:" in str(
                    rule.declarations
                ):
                    color = str(rule.declarations[0].value[0].value)
                    break

        if color[0] == "#":
            color = color[1:]
        return color


def _html_to_post(soup: BeautifulSoup) -> list[Post]:
    # Work on the articles container
    div = soup.find("div", id="articles_container")
    if not div:
        # No article, blog is empty
        return []

    # Get all div inside it with the id starting with a 'a-'
    divs = div.find_all("div", id=lambda value: value and value.startswith("a-"))

    posts = []
    for div in divs:
        text = _get_post_text(div)
        image = _get_post_image(div)
        date = _get_post_date(div)
        title = _get_post_title(div)

        post = Post(text=text, image=image, date=date, title=title)
        posts.append(post)
    return posts


def _get_post_title(soup: BeautifulSoup):
    return soup.find("a").get_text()


def _get_post_text(soup: BeautifulSoup):
    text_container = soup.find("div", class_="text-image-container")
    return text_container


def _get_post_image(soup: BeautifulSoup):
    image_container = soup.find("div", class_="image-container")
    if image_container is None:
        return None

    image = image_container.find("img")
    if image is None:
        return None

    return image.get("src")


def _get_post_date(soup: BeautifulSoup):
    date = soup.find("time", itemprop="dateCreated")
    return date.get_text()
