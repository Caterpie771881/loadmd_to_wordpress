import os
import json
import re
import markdown
import pymdownx
import requests
from utils.argsparser import args
from utils.extensions import (
    replace_img_address,
    fix_codeblock_indentation,
    fix_c_cpp,
    delete_unsupport_languages,
    add_copy_support,
    write_to_tail,
    imgpath_to_imgname,
)
import utils.crypto


def upload_file(file_path, url, password, target):
    """与服务端交互, 进行单文件上传"""
    password, key = utils.crypto.encryption_password(password)
    with open(file_path, 'rb') as f:
        files = {'uploaded_file': (file_path, f)}
        response = requests.post(
            url,
            files=files,
            data={
                "password": password,
                "key": key,
                "target": target,
                "command": "save",
                }
            )
    message = response.headers['message']
    if message:
        if message == "ok":
            print(f"[*]upload \"{file_path}\" success")
            return True
        print(f"[!]fail to upload \"{file_path}\", error: {message}")
        return False
    raise ConnectionError("can't get webshell's respond, please check your config and webshell")


def check_file(filename, url, password, target):
    """与服务端交互, 检查指定路径下是否存在与 filename 同名文件"""
    password, key = utils.crypto.encryption_password(password)
    response = requests.post(
        url,
        data={
            "password": password,
            "key": key,
            "filename": filename,
            "target": target,
            "command": "check",
            }
    )
    message = response.headers['message']
    if message:
        if message == "exist":
            return True
        elif message == "not exist":
            return False
        raise Exception(f"[!]fail to check file \"{filename}\", error: {message}")
    raise ConnectionError("can't get webshell's respond, please check your config and webshell")


def yes_or_no(string, max_time:int=2, default:bool=False):
    if max_time > 0:
        for _ in range(max_time):
            input_ = input(string).lower()
            if input_ == "y":
                return True
            if input_ == "n":
                return False
        return default
    while True:
        input_ = input(string).lower()
        if input_ == "y":
            return True
        if input_ == "n":
            return False


def analysis_folder(path) -> tuple:
    """解析路径下的 md 文件与图片文件情况"""
    img_list = []
    markdown_name = ''
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file():
                file_name = entry.name
                file_type = file_name.split('.')[-1]
                # get markdown_name
                if file_type == "md":
                    print(f"[*]find markdown file:{file_name}")
                    markdown_name = file_name[:-3]
                # get img_list
                elif file_type in support_img_type:
                    print(f"[*]find image file:{file_name}")
                    img_list.append(file_name)
    if markdown_name == '':
        raise Exception("markdown file not found")
    return img_list, markdown_name


def handling_markdown(markdown_path: str, extensions: list = []) -> str:
    """处理 markdown 文件内容, 返回处理后的文本"""
    with open(markdown_path, "r", encoding="utf-8") as file:
        file_str = file.read()
        for extension in extensions:
            file_str = extension.run(file_str)
    return file_str


def md_to_html(md_str: str, ouput_path: str, extensions: list = []):
    """将 md 文本转换为 html 后写入指定路径"""
    html = markdown.markdown(md_str,extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.fenced_code',
        'markdown.extensions.toc',
        'pymdownx.mark',
        'pymdownx.tilde',
        'pymdownx.tasklist'])

    for extension in extensions:
        html = extension.run(html)
    
    with open(ouput_path, "w", encoding="utf-8") as file:
        file.write(html)


def upload_list(file_list: list, base_path: str):
    """尝试上传列表中的所有文件, 上传之前检查是否存在同名文件"""
    for file_name in file_list:
        file_path = os.path.join(base_path, file_name)
        # check if a file with the same name already exists
        match args.over_write:
            case True:
                pass
            case False:
                if check_file(file_name, webshell_address, webshell_password, target):
                    continue
            case _:
                if check_file(file_name, webshell_address, webshell_password, target):
                    if not yes_or_no(f"{file_name} has exist, do you want to overwrite it? (Y/N):"):
                        continue
        # upload the file
        if upload_file(file_path, webshell_address, webshell_password, target):
            continue
        if not yes_or_no("Do you want to countinue? (Y/N):"):
            break


def sniffer_imgs(markdown_path) -> list:
    """嗅探单文件中引用的本地图片, 检查文件是否存在, 并返回绝对路径列表"""
    img_list = []
    markdown_dir = os.path.dirname(markdown_path)

    def find_imgs_by(regex):
        nonlocal img_list
        img_paths: list[str] = re.findall(regex, file_str)
        for path in img_paths:
            abspath = os.path.abspath(os.path.join(markdown_dir, path))
            if os.path.isfile(abspath) and path.split('.')[-1] in support_img_type:
                img_list.append(abspath)
                print(f"[*]sniff img: {abspath}")
            else:
                print(f"[?]The file does not exist or the file format is not supported: {path}")
    
    with open(markdown_path, "r", encoding="utf-8") as file:
        file_str = file.read()
        find_imgs_by(r"!\[.*?\]\((?!http)(.*?)\)")
        find_imgs_by(r"<img src=\"(?!http)(.*?)\".*?/>")
    return img_list


def submit_work(path: str):                                                                                                              
    def add_draft(url: str, title: str, content: str):
        """通过 restapi 发布文章草稿"""
        resp = requests.post(
            url=url.strip('/')+"/wp-json/wp/v2/posts",
            headers={
                "Authorization": utils.crypto.authorization(
                    restapi_user,
                    restapi_token
                ),
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "title": title,
                "content": content,
                "status": "draft",
            })
        )
        if resp.ok:
            print(f"[*]已发表草稿 {title}")
    def edit_post(url: str, post_id: int, options: dict):
        """通过 restapi 修改文章内容"""
        resp = requests.put(
            url=url.strip('/')+f"/wp-json/wp/v2/posts/{post_id}",
            headers={
                "Authorization": utils.crypto.authorization(
                    restapi_user,
                    restapi_token
                ),
                "Content-Type": "application/json"
            },
            data=json.dumps(options)
        )
        if resp.ok:
            print(f"[*]已修改文章 {options['title']}")
    title, _ = os.path.splitext(os.path.basename(path))
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    if isinstance(args.submit, int):
        edit_post(
            url=restapi_website,
            post_id=args.submit,
            options={'title':title, 'content':content}
        )
    elif args.submit:
        add_draft(
            url=restapi_website,
            title=title,
            content=content
        )


def loadmd_from_folder(path):
    """当路径为文件夹时的处理逻辑"""
    img_list, markdown_name = analysis_folder(path)
    markdown_path = os.path.join(path, markdown_name) + ".md"
    html_path = os.path.join(path, markdown_name) + ".html"
    file_str = handling_markdown(markdown_path, extensions=[
        replace_img_address(img_src=img_src),
        fix_codeblock_indentation(),
        fix_c_cpp(),
        delete_unsupport_languages(support_languages=support_languages),
    ])
    md_to_html(file_str, html_path, extensions=[
        add_copy_support(),
        write_to_tail(word="\n<script>hljs.highlightAll();</script>"),
    ])
    print(f"[*]\"{markdown_path}\" => \"{html_path}\"")
    upload_list(img_list, path)
    submit_work(html_path)


def loadmd_from_file(path):
    """当路径为单文件时的处理逻辑"""
    markdown_path = path
    html_path = markdown_path[:-3] + ".html"
    normal_mode_extensions = [
        fix_codeblock_indentation(),
        fix_c_cpp(),
        delete_unsupport_languages(support_languages=support_languages),
    ]
    # sniffer mode
    if args.sniffer:
        img_list = sniffer_imgs(markdown_path)
        file_str = handling_markdown(markdown_path, extensions=[
            imgpath_to_imgname(),
            replace_img_address(img_src=img_src),
            ] + normal_mode_extensions
        )
        upload_list(img_list, path)
    # normal mode
    else:
        file_str = handling_markdown(markdown_path, extensions=normal_mode_extensions)
    md_to_html(file_str, html_path, extensions=[
        add_copy_support(),
        write_to_tail(word="\n<script>hljs.highlightAll();</script>"),
    ])
    print(f"[*]\"{markdown_path}\" => \"{html_path}\"")
    submit_work(html_path)


def loadmd_from(path):
    if os.path.isdir(path):
        print(f"[*]Processing folder: \"{path}\"")
        loadmd_from_folder(path)
    elif os.path.isfile(path) and path[-3:] == ".md":
        print(f"[*]Processing file: \"{path}\"")
        loadmd_from_file(path)
    else:
        print(f"[!]Illegal path: \"{path}\", please check the config")


# load config
if args.config:
    config_path = args.config
else:
    config_path = "config.json"
    print("[!]please specify the config file path with [-c] or [--config]")
try:
    config_file = open(config_path, "r", encoding="utf-8")
    config = json.loads(config_file.read())
    path = config["path"]
    webshell_address = config["webshell"]["address"]
    webshell_password = config["webshell"]["password"]
    img_src = config["img_src"]
    target = config["target"]
    support_img_type = config["support"]["img_type"]
    support_languages = config["support"]["languages"]
    restapi_website = config["restapi"]["website"]
    restapi_user = config["restapi"]["user"]
    restapi_token = config["restapi"]["token"]
    print("[*]load config success")
except:
    raise Exception("[!]fail to load config")

if args.path:
    path = args.path

if isinstance(path, list):
    # 批处理
    for path_ in path:
        loadmd_from(path_)
else:
    loadmd_from(path)
