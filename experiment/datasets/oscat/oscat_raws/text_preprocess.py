import re
def extract_title_content(text):
    # 正则表达式匹配标题格式，并捕获实际内容
    pattern = r'^\d+\.\d+\.\s*([A-Z_]+)$'
    match = re.match(pattern, text)
    if match:
        return match.group(1)  # 返回捕获的实际内容
    return None

def split_titles_and_content(text):
    # 正则表达式匹配标题和内容
    pattern = r'(\d+\.\d+\.\s*[A-Z_]+)\n(.*?)(?=\n\d+\.\d+\.\s*[A-Z_]+|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)
    return [(title.strip(), content.strip()) for title, content in matches]

def keep_description(name,text):
    # 找到name串第一次出现的位置
    position = text.find(name)
    _ = text[:position]
    description = text[position:]
    
    position = description.find("Example")
    if position != -1:
        description = description[:position]
    return description

# 拆分标题和内容
with open("oscat_basic333_en_processed.txt","r") as fp:
    text = fp.read()
    titles_and_contents = split_titles_and_content(text)
    # 打印结果
    cnt = 0
    for title, content in titles_and_contents:
        cnt += 1
        title = extract_title_content(title)
        with open(f"processed/{title}.txt","w") as fp:
            content = keep_description(title,content)
            if  len(content) < 10:
                print(title,content)
            fp.write(content)
    print(cnt)