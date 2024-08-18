# loadmd_to_wordpress

该项目用于将本地的 markdown 文件快速迁移至 wordpress 系统

# 使用方式

step1. 安装 python 脚本所需库

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
