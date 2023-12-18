# EpubFormer
## 主要功能
1. 按顺序重命名 .epub 文件中的图片；
2. 将 .zip 中的图片缩放后重新打包

## 说明
- 从 vol.moe 上下载的 epub 文件中，image 文件夹的图片文件名是不规则的，此脚本可以按页码重新命名图片文件。
这样可以直接把图片文件提取出来，按文件名排序，即可摆脱 epub 阅读器的限制。
- 从某些网站获取到的漫画图片过大，此脚本可以将 zip 包中的图片缩放后重新打包到 zip。

## 使用方法
### EpubFormer
1. 将 epub 文件复制到 [input](/input) 目录；
2. 运行 [main.py](main.py)；
3. 脚本自动转换 input 中的所有 epub 文件；
4. 转换后的文件保存在 [output](/output) 目录。

### ZipImgResizer
1. 将 zip 文件复制到 [input](/input) 目录；
2. 编辑 [local_properties.py](/common/local_properties.py)，设置缩放比例 `RESIZE_SCALE` （如 0.6 为缩放到 60%）；
3. 运行 [main.py](main.py)；
4. 脚本自动转换 input 中的所有 zip 文件；
5. 转换后的文件保存在 [output](/output) 目录。

## 已知问题
- 图片数超过 1000 可能还是无法排序，遇见了再说；
- 只扒出了 vol.moe 下载到的 epub 的结构，别的 epub 可能读不到 opf；（小问题不够用再改）
- Windows 打包的 zip 在解压时可能出现乱码，目前只是采用了重命名的方式，崩了再改。
