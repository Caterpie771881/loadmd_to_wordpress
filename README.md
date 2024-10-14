# loadmd_to_wordpress

该项目用于将本地的 markdown 文件快速迁移至 wordpress 系统

# 项目说明

该项目支持 python 3.10 及以上版本

## 目录结构

```
loadmd_to_wordpress
├── config.json           # 客户端配置示例
├── License
├── loadmd_plugin
│   ├── loadmd_plugin.php # 插件入口
│   ├── setting_page.php  # 设置页面
│   └── webshell.php      # 实现了上传功能的 webshell
├── loadmd.py             # 客户端入口
├── README.md
├── requirements.txt
└── utils
    ├── argsparser.py     # 负责解析命令行参数
    ├── crypto.py         # 密码学工具
    └── extensions.py     # 文本处理扩展
```

## 配置文件说明

### path

> 接受 3 种参数:
>
> 1.  存放了 markdown 与引用图片的文件夹, 如: "D://blog_01/"
> 2.  markdown 单文件, 如: "D://blog_02.md"
> 3.  使用数组包含多个 1/2 类型参数, 如: ["D://blog_01/", "D://blog_02.md"]

### webshell

> address
>
> 在 "md 上传助手" 中配置的 webshell 访问入口
>
> password
>
> 在 "md 上传助手" 中配置的 webshell 访问密码

### img_src

> markdown 访问引用图片时的 URL 前缀
>
> 如: 当该配置项为 "https://www.example.com/myimg/" 时
>
> 脚本将会把 !\[img](img_01.jpg) 替换为
>
> !\[img](https://www.example.com/myimg/img_01.jpg)

### target

> 服务器存放文章引用的图片的绝对路径

### support

> img_type
>
> 支持的图片格式
>
> languages
>
> 代码高亮中支持的语言(不支持的语言将会统一使用纯文本的高亮)

## 客户端参数说明

```
-h, --help          获取帮助
-c, --config        指定配置文件位置
-p, --path          强制指定 markdown 文件/文件夹路径(会覆盖 config 的配置)
-ow, --over-write   为 true 时强制覆写重名文件, 为 false 时强制不覆写重名文件
--sniffer           添加此参数时开启 "嗅探模式"
(嗅探模式: 仅对单文件 path 生效, 自动探查 md 引用的本地图片路径并进行改写、上传)
```

# 快速开始

step1. 使用 python3.10+ 版本, 并安装脚本所需库

```sh
pip install -r requirements.txt
```

step2. 将 loadmd_plugin 文件夹打包为 zip 文件并将其安装至 wordpress

step3. 在 wordpress 后台为 `md 上传助手` 配置必要参数

step4. 编辑 config.json 中的配置项

example

```json
{
  "path": "D:\\markdown_folder",
  "webshell": {
    "address": "https://www.example.com/my_webshell",
    "password": "admin123"
  },
  "img_src": "http://www.example.com/wp-content/uploads/myimgs/",
  "target": "/www/wwwroot/my_wordpress/wp-content/uploads/myimgs/",
  "support": {
    "img_type": ["jpg", "png", "gif", "jpeg", "webp"],
    "languages": ["html", "css", "javascript", "http", "bash"]
  }
}
```

step5. 使用下面的命令来运行 markdown 转换脚本

```sh
python loadmd.py -c config.json
```

脚本将会在 md 文件相同的路径下生成对应的 html 文件

# 未来计划

1. ~~添加功能: 引入时间戳防止重放攻击~~ (已实现)

2. ~~插件添加 "导出 config.json" 功能~~ (已实现)

3. ~~插件添加 "check webshell_address" 功能, 检查地址是否可用~~ (已实现)

4. 添加功能: 客户端在导出 html 时自动上传至 wordpress 并创建文章草稿
