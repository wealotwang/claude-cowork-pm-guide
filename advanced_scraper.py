import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re

def scrape_full_content():
    url = "http://47.93.225.26/pmlearn.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"正在获取网页内容: {url} ...")
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    
    if response.status_code != 200:
        print(f"获取网页失败，状态码: {response.status_code}")
        return
    
    print("正在解析网页结构...")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 移除不需要的标签（脚本、样式、SVG图标等，这些会干扰Markdown生成）
    for tag in soup(['script', 'style', 'svg', 'noscript', 'meta', 'head', 'title']):
        tag.decompose()
    
    # 尝试找到主要内容区域。如果不确定，就使用整个 body
    main_content = soup.find('body')
    if not main_content:
        main_content = soup
        
    # 转换为 Markdown
    print("正在将 HTML 转换为 Markdown...")
    markdown_content = md(
        str(main_content),
        heading_style="ATX",
        bullets="-",
        strip=['img'], # 如果需要保留图片，可以移除这一行
        autolinks=False
    )
    
    # 清理和美化 Markdown 文本
    # 1. 移除过多的空行（将3个以上的空行替换为2个）
    markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
    # 2. 去除每行开头和结尾的多余空格
    lines = [line.strip() if not line.startswith(' ') else line.rstrip() for line in markdown_content.split('\n')]
    
    # 重新组合
    cleaned_content = '\n'.join(lines)
    
    # 写入文件
    output_file = "pmlearn_full.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Claude Cowork 自学路线 (完整深度抓取版)\n\n")
        f.write("> 本文档由 Python 爬虫 (BeautifulSoup4 + Markdownify) 自动生成，完整保留了网页的所有文本、层级结构和超链接。\n\n")
        f.write(cleaned_content)
        
    print(f"爬取完成！所有内容已完整保存至: {output_file}")

if __name__ == "__main__":
    scrape_full_content()
