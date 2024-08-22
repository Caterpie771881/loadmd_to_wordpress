"""处理 md 和 html 的扩展"""
import re

class Extension:
    def __init__(self, **kwargs) -> None:
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])
    def run(self, file_str: str) -> str:
        return file_str


class replace_img_address(Extension):
    """将 md 本地图片地址替换为网址形式"""
    def run(self, file_str: str) -> str:
        regex = r"!\[.*?\]\((?!http)(.*?)\)"
        subst = f"![img]({self.img_src}\\1)"
        file_str = re.sub(regex, subst, file_str, 0, re.MULTILINE)
        regex = r"<img src=\"(?!http)(.*?)\"(.*?)/>"
        subst = f"<img src=\"{self.img_src}\\1\"\\2/>"
        file_str = re.sub(regex, subst, file_str, 0, re.MULTILINE)
        print("[*]已替换图片地址")
        return file_str


class fix_codeblock_indentation(Extension):
    """修复异常的代码块缩进"""
    def run(self, file_str: str) -> str:
        regex = r"^ +```(.*)"
        subst = "```\\1"
        file_str = re.sub(regex, subst, file_str, 0, re.MULTILINE)
        print("[*]已修复异常的代码块缩进")
        return file_str

class fix_c_cpp(Extension):
    """将 c_cpp 标记替换为 cpp"""
    def run(self, file_str: str) -> str:
        regex = r"```c_cpp"
        subst = "```cpp"
        file_str = re.sub(regex, subst, file_str, 0, re.MULTILINE)
        print("[*]已修复不规范的 'c_cpp' 标记")
        return file_str


class delete_unsupport_languages(Extension):
    """去除不支持的语言格式"""
    def run(self, file_str: str) -> str:
        regex = r"^```(.+)"
        def check_language(match: re.Match):
            language = match.group(1)
            if language not in self.support_languages:
                language = ""
            return f"```{language}"
        file_str = re.sub(regex, check_language, file_str, 0, re.MULTILINE)
        print("[*]已去除不支持的语言格式")
        return file_str


class add_copy_support(Extension):
    """添加 copy 支持"""
    def run(self, file_str) -> str:
        regex = r"<pre><code(.*?)>"
        num = 0
        def add_copy_id(match: re.Match):
            nonlocal num
            element = f"<pre><code{match.group(1)} id=copy{num}>"
            num += 1
            return element
        html = re.sub(regex, add_copy_id, html, 0, re.MULTILINE)
        print("[*]已添加 copy 支持")
        return file_str


class write_to_tail(Extension):
    """将指定文本写入文件末尾"""
    def run(self, file_str) -> str:
        file_str += self.word
        return file_str
