# Skyblog Archiver 📰
Archive skyrock.com blogs in a readable HTML format.

## Context
Skyrock.com was one of the first major social media of the 21st century, mainly used in French-speaking countries.  
Everyone could create its one blog and post whatever they wants in it. The site offers multiple customization options to make a colorful webpage.  

Skyblogs were closed the 2023/08/21, [you can read more about it here](https://web.archive.org/web/20230818160652/https://lequipe-skyrock.skyrock.com/).


# Installation & Usage
You will need at least Python3.11 to start the software. You can change parameters in the `config.ini` file.  

Install the needed packages :
```shell
$ pip install -r requirements.txt
```
Then, paste blogs URL or username in the file `list_users.txt`, one per line.  

Finally, run the software :
```shell
$ python src/__main__.py
```

Archived blogs will be saved in the `archives` directory.


# Known issues
* Skyblog offer too many colors customization in multiple CSS files, making it very difficult to scrap proper colors.
* Comments archiving have not been implemented.


# Acknowledgments
Thank you for the original work published by [Eric Philippe](https://github.com/Eric-Philippe/Skyblog_Archiver/tree/main) which mainly inspired me to write this software.
