import os
import argparse
import json
import re
import markdown
import pymdownx
import requests

def upload_file(file_path, url, password, target):
    with open(file_path, 'rb') as f:
        files = {'uploaded_file': (file_path, f)}
        response = requests.post(
            url,
            files=files,
            data={
                "password": password,
                "target": target,
                }
            )
    message = response.headers['message']
    #TODO: 添加各个 message 的处理逻辑, 细化 logging
    #TODO: 检测是否有重名文件, 添加选项: 是否覆盖文件
    if message:
        if message == "ok":
            print(f"[*]upload \"{file_path}\" success")
        else:
            print(f"[!]fail to upload \"{file_path}\", error: {message}")
    else:
        print("[?]can't get webshell's answer, please check you config")

argparser = argparse.ArgumentParser()
argparser.add_argument("-c", "--config", help="load you config")
args = argparser.parse_args()

# load config
if args.config:
    try:
        config_file = open(args.config, "r", encoding="utf-8")
        config = json.loads(config_file.read())
        path = config["path"]
        webshell_address = config["webshell"]["address"]
        webshell_password = config["webshell"]["password"]
        img_src = config["img_src"]
        target = config["target"]
        support_img_type = config["support"]["img_type"]
        support_languages = config["support"]["languages"]
        print("[*]load config success")
    except:
        raise "[!]fail to load config"
else:
    raise "[!]please specify the config file path with [-c] or [--config]"

#TODO: 添加单文件支持
#TODO: 添加批量处理支持
img_list = []
markdown_name = ''
with os.scandir(path) as entries:
    for entry in entries:
        if entry.is_file():
            file_name = entry.name
            file_type = file_name.split('.')[-1]
            # get markdown_name
            if file_type == "md":
                print(f"[*]find a markdown file:{file_name}")
                markdown_name = file_name[:-3]
            # get img_list
            elif file_type in support_img_type:
                print(f"[*]find an image file:{file_name}")
                img_list.append(file_name)
if markdown_name == '':
    raise "markdown file not found"

markdown_path = os.path.join(path, markdown_name) + ".md"
html_path = os.path.join(path, markdown_name) + ".html"

with open(markdown_path, "r", encoding="utf-8") as file:
    file_str = file.read()

    regex = r"!\[.*?\]\((?!http)(.*?)\)"
    subst = f"![img]({img_src}\\1)"
    file_str = re.sub(regex, subst, file_str, 0, re.MULTILINE)
    regex = r"<img src=\"(?!http)(.*?)\"(.*?)/>"
    subst = f"<img src=\"{img_src}\\1\"\\2/>"
    file_str = re.sub(regex, subst, file_str, 0, re.MULTILINE)
    print("[*]已替换图片地址")

    regex = r"^ +```(.*)"
    subst = "```\\1"
    file_str = re.sub(regex, subst, file_str, 0, re.MULTILINE)
    print("[*]已修复异常的代码块缩进")

    regex = r"```c_cpp"
    subst = "```cpp"
    file_str = re.sub(regex, subst, file_str, 0, re.MULTILINE)
    print("[*]已修复不规范的 'c_cpp' 标记")
    
    regex = r"^```(.+)"
    def check_language(match: re.Match):
        language = match.group(1)
        if language not in support_languages:
            language = ""
        return f"```{language}"
    file_str = re.sub(regex, check_language, file_str, 0, re.MULTILINE)
    print("[*]已去除不支持的语言格式")

html = markdown.markdown(file_str,extensions=[
    'markdown.extensions.extra',
    'markdown.extensions.fenced_code',
    'markdown.extensions.toc',
    'pymdownx.mark',
    'pymdownx.tilde'])

regex = r"<pre><code(.*?)>"
num = 0
def add_copy_id(match: re.Match):
    global num
    element = f"<pre><code{match.group(1)} id=copy{num}>"
    num += 1
    return element
html = re.sub(regex, add_copy_id, html, 0, re.MULTILINE)
print("[*]已添加 copy 支持")

with open(html_path, "w", encoding="utf-8") as file:
    file.write(html)
    file.write("\n<script>hljs.highlightAll();</script>",)
print(f"[*]\"{markdown_path}\" => \"{html_path}\"")

for img in img_list:
    img_path = os.path.join(path, img)
    upload_file(img_path, webshell_address, webshell_password, target)