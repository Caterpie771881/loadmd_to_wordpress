import os
import json
import markdown
import pymdownx
import requests
import time
from utils.argsparser import args
from utils.extensions import (
    replace_img_address,
    fix_codeblock_indentation,
    fix_c_cpp,
    delete_unsupport_languages,
    add_copy_support,
    write_to_tail,
)


def upload_file(file_path, url, password, target):
    """与服务端交互, 进行单文件上传"""
    with open(file_path, 'rb') as f:
        files = {'uploaded_file': (file_path, f)}
        response = requests.post(
            url,
            files=files,
            data={
                "password": password,
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
    raise "can't get webshell's respond, please check your config and webshell"


def check_file(filename, url, password, target):
    """与服务端交互, 检查指定路径下是否存在与 filename 同名文件"""
    response = requests.post(
        url,
        data={
            "password": password,
            "filename": filename,
            "target": target,
            "command": "check",
            }
    )
    message = response.headers['message']
    if message:
        if message == "exist":
            return True
        return False
    raise "can't get webshell's respond, please check your config and webshell"


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

#TODO: 添加流量加密功能, 引入时间戳校验防止 webshell 被重放攻击
def encryption_password(password): ...


def analysis_folder(path) -> list:
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
                    print(f"[*]find a markdown file:{file_name}")
                    markdown_name = file_name[:-3]
                # get img_list
                elif file_type in support_img_type:
                    print(f"[*]find an image file:{file_name}")
                    img_list.append(file_name)
    if markdown_name == '':
        raise "markdown file not found"
    return {
        "img_list": img_list,
        "markdown_name": markdown_name
    }


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
        'pymdownx.tilde'])

    for extension in extensions:
        html = extension.run(html)
    
    with open(ouput_path, "w", encoding="utf-8") as file:
        file.write(html)


def upload_list(file_list: list):
    """尝试上传列表中的所有文件, 上传之前检查是否存在同名文件"""
    for file_name in file_list:
        file_path = os.path.join(path, file_name)
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
    """嗅探单文件中引用的本地图片, 检查文件是否存在, 并返回路径列表"""
    img_list = []
    with open(markdown_path, "r", encoding="utf-8") as file:
        file_str = file.read()
    return img_list


def loadmd_from_folder(path):
    """当路径为文件夹时的处理逻辑"""
    img_list, markdown_name = analysis_folder(path)
    markdown_path = os.path.join(path, markdown_name) + ".md"
    html_path = os.path.join(path, markdown_name) + ".html"
    file_str = handling_markdown(markdown_path, extensions=[
        replace_img_address(img_src=img_src),
        fix_codeblock_indentation,
        fix_c_cpp,
        delete_unsupport_languages(support_languages=support_languages),
    ])
    md_to_html(file_str, html_path, extensions=[
        add_copy_support,
        write_to_tail(word="\n<script>hljs.highlightAll();</script>"),
    ])
    print(f"[*]\"{markdown_path}\" => \"{html_path}\"")
    upload_list(img_list)


def loadmd_from_file(path):
    """当路径为单文件时的处理逻辑"""
    markdown_path = path
    html_path = markdown_path[:-3] + ".html"
    if args.sniffer:
        img_list = sniffer_imgs(markdown_path)
        file_str = handling_markdown(markdown_path, extensions=[
            replace_img_address(img_src=img_src),
            fix_codeblock_indentation,
            fix_c_cpp,
            delete_unsupport_languages(support_languages=support_languages),
        ])
        upload_list(img_list)
    else:
        file_str = handling_markdown(markdown_path, extensions=[
            fix_codeblock_indentation,
            fix_c_cpp,
            delete_unsupport_languages(support_languages=support_languages),
        ])
    md_to_html(file_str, html_path, extensions=[
        add_copy_support,
        write_to_tail(word="\n<script>hljs.highlightAll();</script>"),
    ])
    print(f"[*]\"{markdown_path}\" => \"{html_path}\"")


def loadmd_from(path):
    if os.path.isdir(path):
        print(f"[*]正在处理文件夹: \"{path}\"")
        loadmd_from_folder(path)
    elif os.path.isfile(path) and path[-3:] == ".md":
        print(f"[*]正在处理单文件: \"{path}\"")
        loadmd_from_file(path)
    else:
        print(f"[!]非法路径: \"{path}\", 请检查配置文件")


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

if path is list:
    # 批处理
    for path_ in path:
        loadmd_from(path_)
else:
    loadmd_from(path)
