import os
import shutil

from common import save_picture


class SkyblogWriter:
    def __init__(
        self,
        username: str,
        path_dir_archive_user: str,
        path_template: str,
        articles,
        title: str,
        description: str,
        max_page_number: int,
        url_background: str,
        url_profile_picture: str,
        color_background: str,
        color_theme: str,
        color_block_title: str,
        color_text_title: str,
        color_articles_background: str,
    ):
        self.username = username
        self.path_dir_archive_user = path_dir_archive_user
        self.path_template = path_template
        self.articles = articles
        self.title = title
        self.description = description
        self.max_page_number = max_page_number
        self.url_background = url_background
        self.url_profile_picture = url_profile_picture
        self.color_background = color_background
        self.color_theme = color_theme
        self.color_block_title = color_block_title
        self.color_text_title = color_text_title
        self.color_articles_background = color_articles_background

    def archive(self):
        self.init_template()
        self.save_background_picture()
        self.save_profile_picture()
        self.fill_index_html()

    def init_template(self):
        """Copy the template folder"""
        shutil.copytree(
            self.path_template, self.path_dir_archive_user, dirs_exist_ok=True
        )

    def save_background_picture(self):
        if self.url_background is None:
            # No background found by the reader, skipping
            return

        save_picture(
            path_dir_output=os.path.join(self.path_dir_archive_user, "img"),
            url=self.url_background,
            filename="background.jpg",
        )

    def save_profile_picture(self):
        if self.url_profile_picture is None:
            # No profile picture found by the scrapper
            return

        save_picture(
            path_dir_output=os.path.join(self.path_dir_archive_user, "img"),
            url=self.url_profile_picture,
            filename="profile_picture.jpg",
        )

    def fill_index_html(self):
        """
        Replace every {{ username }} in the index.html file with the username
        And fill the div with the id "posts" with the posts
        """
        with open(self.path_dir_archive_user + "/index.html") as fp_html:
            html_content = fp_html.read()
        with open(self.path_dir_archive_user + "/styles.css") as fp_css:
            css_content = fp_css.read()

        # Replace the {{ username }} with the username
        html_content = html_content.replace("{{ username }}", self.username)

        # Fill the div with the id "posts" with the posts
        posts_html = ""
        for post in self.articles:
            posts_html += post.to_html(self.path_dir_archive_user)
        html_content = html_content.replace("{{ posts }}", posts_html)

        # Add the background to the body html element
        html_content = html_content.replace(
            "{{ path_file_background }}",
            os.path.join(self.path_dir_archive_user, "img", "background.jpg"),
        )

        # Fill the background with the proper color
        # Overwrite wallpaper, thus check beforehand if it exists
        html_content = html_content.replace(
            "{{ background_color }}",
            f"background: #{self.color_background};" if not self.url_background else "",
        )

        # Set theme color
        html_content = html_content.replace(
            "{{ theme_color_with_attribute }}", f"color: #{self.color_theme}"
        )
        html_content = html_content.replace("{{ theme_color }}", f"#{self.color_theme}")
        css_content = css_content.replace("{{ theme_color }}", f"#{self.color_theme}")

        # Set title
        html_content = html_content.replace("{{ title }}", self.title)

        # Set the description
        html_content = html_content.replace("{{ description }}", self.description)

        # Fill all titles with the proper color
        html_content = html_content.replace(
            "{{ color_block_title }}", self.color_block_title
        )

        # Fill all titles text with the proper color
        html_content = html_content.replace(
            "{{ color_text_title }}", self.color_text_title
        )

        # Fill all articles background with the proper color
        html_content = html_content.replace(
            "{{ color_articles_background }}", self.color_articles_background
        )

        with open(self.path_dir_archive_user + "/index.html", "w") as fp_html:
            fp_html.write(html_content)
        with open(self.path_dir_archive_user + "/styles.css", "w") as fp_css:
            fp_css.write(css_content)
