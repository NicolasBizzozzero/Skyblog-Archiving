import os

from bs4 import Tag

from common import save_picture


class Post(object):
    """
    Skyblog Post class
    """

    def __init__(self, text: Tag, image: str, date: str, title: str):
        self.text = text
        self.image_url = image
        self.date = date
        self.title = title

    def to_html(self, folder_name: str):
        html_content = '<div class="post" style="background-color: #{{ color_articles_background }}">'
        if self.image_url is not None:
            # Locally save the image inside the img folder itself inside the folderName
            img_name = self.image_url.split("/")[-1]
            save_picture(
                path_dir_output=os.path.join(folder_name, "img"), url=self.image_url
            )
            # Add the title to the html
            html_content += f'<h2 style="background-color: #{{{{ color_block_title }}}};color: #{{{{ color_text_title }}}};display:block;margin:0;padding:0;text-align:center;">{self.title}</h2>'

            # Add the image to the html
            html_content += f'<a href="img/{img_name}" class="lightbox" data-lightbox="post-images"><img src="img/{img_name}" /></a>'

        # Add the text to the html
        html_content += self.text.prettify()

        # Add the date to the html
        html_content += '<p class="date">' + self.date + "</p>"
        html_content += "</div>"

        return html_content
