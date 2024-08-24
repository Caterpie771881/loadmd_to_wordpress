"""处理 md 和 html 的扩展"""
import re
import os

class Extension:
    _need = []
    def __init__(self, **kwargs) -> None:
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])
    def run(self, file_str: str) -> str:
        for arg in self._need:
            if not hasattr(self, arg):
                raise AttributeError("the Extension '%s' need attribute '%s'"
                                     % (self.__class__.__name__, arg))
        return self.main(file_str)
    def main(self, file_str: str) -> str:
        return file_str


class replace_img_address(Extension):
    """将 md 本地图片地址替换为网址形式"""
    _need = ["img_src"]

    def main(self, file_str: str) -> str:
        regex = r"!\[.*?\]\((?!http)(.*?)\)"
        subst = f"![img]({self.img_src}\\1)"
        file_str = re.sub(regex, subst, file_str, 0, re.MULTILINE)
        regex = r"<img src=\"(?!http)(.*?)\"(.*?)/>"
        subst = f"<img src=\"{self.img_src}\\1\"\\2/>"
        file_str = re.sub(regex, subst, file_str, 0, re.MULTILINE)
        print("[*]Replaced picture address")
        return file_str


class fix_codeblock_indentation(Extension):
    """修复异常的代码块缩进"""
    def main(self, file_str: str) -> str:
        regex = r"^ +```(.*)"
        subst = "```\\1"
        file_str = re.sub(regex, subst, file_str, 0, re.MULTILINE)
        print("[*]Exception code block indentation has been fixed")
        return file_str


class fix_c_cpp(Extension):
    """将 c_cpp 标记替换为 cpp"""
    def main(self, file_str: str) -> str:
        regex = r"```c_cpp"
        subst = "```cpp"
        file_str = re.sub(regex, subst, file_str, 0, re.MULTILINE)
        print("[*]Fixed non-standard 'c_cpp' tags")
        return file_str


class delete_unsupport_languages(Extension):
    """去除不支持的语言格式"""
    _need = ["support_languages"]

    def check_language(self, match: re.Match):
        language = match.group(1)
        if language not in self.support_languages:
            language = ""
        return f"```{language}"
    
    def main(self, file_str: str) -> str:
        regex = r"^```(.+)"
        file_str = re.sub(regex, self.check_language, file_str, 0, re.MULTILINE)
        print("[*]Unsupported language formats have been removed")
        return file_str


class add_copy_support(Extension):
    """添加 copy 支持"""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.num = 0
    
    def add_copy_id(self, match: re.Match):
        element = f"<pre><code{match.group(1)} id=copy{self.num}>"
        self.num += 1
        return element
    
    def main(self, file_str) -> str:
        regex = r"<pre><code(.*?)>"
        self.num = 0
        file_str = re.sub(regex, self.add_copy_id, file_str, 0, re.MULTILINE)
        print("[*]Copy support has been added")
        return file_str


class write_to_tail(Extension):
    """将指定文本写入文件末尾"""
    _need = ["word"]
    def main(self, file_str) -> str:
        file_str += self.word
        return file_str


class imgpath_to_imgname(Extension):
    """将完整路径替换为仅文件名(为嗅探模式服务)"""
    def replace_path(self, mode: int = 1):
        def wrap(match: re.Match):
            path = match.group(1)
            name = os.path.basename(path)
            if mode == 1:
                element = f"![img]({name})"
            else:
                element = f"<img src=\"{name}\"{match.group(2)}/>"
            return element
        return wrap
    
    def main(self, file_str) -> str:
        regex = r"!\[.*?\]\((?!http)(.*?)\)"
        file_str = re.sub(regex, self.replace_path(mode=1), file_str, 0, re.MULTILINE)
        regex = r"<img src=\"(?!http)(.*?)\"(.*?)/>"
        file_str = re.sub(regex, self.replace_path(mode=2), file_str, 0, re.MULTILINE)
        print("[*]The full path has been replaced with a filename only")
        return file_str
