import ijson
import json
from decimal import Decimal
import re

# 假设原始数据存储在名为 'nankai_news.json' 的文件中
input_file_path = 'nankai_news.json'
output_file_path = 'nankai_data.json'
duplicates_file_path = 'removed_duplicates.json'
temp_file_path = 'temp_nankai_news.json'

print("开始读取原始数据...")

# 预处理文件内容，添加最外层的方括号并修复格式问题
def clean_json_content(content):
    """清理JSON内容，移除可能导致解析错误的特殊字符"""
    # 移除BOM（Byte Order Mark）
    content = content.lstrip('\ufeff')
    
    # 移除控制字符
    control_chars = ''.join(map(chr, list(range(0, 32)) + list(range(127, 160))))
    control_char_re = re.compile('[%s]' % re.escape(control_chars))
    content = control_char_re.sub('', content)
    
    # 尝试修复可能的格式问题
    content = content.replace('}{', '},{')
    
    return content

with open(input_file_path, 'r', encoding='utf-8') as infile, open(temp_file_path, 'w', encoding='utf-8') as outfile:
    content = infile.read().strip()
    
    # 检查文件是否以 '[' 开头和 ']' 结尾
    if not content.startswith('['):
        content = '[' + content
    if not content.endswith(']'):
        content += ']'
    
    # 清理JSON内容
    content = clean_json_content(content)
    
    outfile.write(content)

print("文件预处理完成，开始解析JSON对象...")

# 创建一个集合用于存储唯一的URL
unique_urls = set()
# 创建一个新的列表用于存储去重后的数据
deduplicated_data = []
# 创建一个列表用于存储被去除的重复数据
removed_duplicates = []

# 使用ijson逐个解析JSON对象
try:
    with open(temp_file_path, 'r', encoding='utf-8') as file:
        parser = ijson.items(file, 'item')
        for item in parser:
            if item['url'] not in unique_urls:
                unique_urls.add(item['url'])
                deduplicated_data.append(item)
                print(f"已处理 URL: {item['url']} 已加入")
            else:
                removed_duplicates.append(item)  # 记录被去除的重复项
                print(f"已处理 URL: {item['url']} 是重复项，已被移除")
except ijson.common.IncompleteJSONError as e:
    print(f"解析错误: {e}")
    # 如果解析失败，尝试跳过有问题的部分并继续解析
    with open(temp_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
        # 解码错误信息，确保它是字符串而不是字节
        error_message = str(e).decode('utf-8') if isinstance(e, bytes) else str(e)
        
        # 尝试找到错误位置并修复
        try:
            error_pos = int(re.search(r'char (\d+)', error_message).group(1))
            content_before_error = content[:error_pos]
            content_after_error = content[error_pos:]
            
            # 尝试修复错误部分
            content_fixed = content_before_error + '}' + content_after_error
            
            # 重新写入临时文件
            with open(temp_file_path, 'w', encoding='utf-8') as outfile:
                outfile.write(content_fixed)
            
            print("尝试修复错误后重新解析...")
            with open(temp_file_path, 'r', encoding='utf-8') as file:
                parser = ijson.items(file, 'item')
                for item in parser:
                    if item['url'] not in unique_urls:
                        unique_urls.add(item['url'])
                        deduplicated_data.append(item)
                        print(f"已处理 URL: {item['url']} 已加入")
                    else:
                        removed_duplicates.append(item)  # 记录被去除的重复项
                        print(f"已处理 URL: {item['url']} 是重复项，已被移除")
        except (AttributeError, ValueError) as ex:
            print(f"无法解析错误位置: {ex}")
            print("跳过此错误并继续解析剩余内容...")

print("去重完成，准备保存结果...")

# 自定义JSON编码器，处理 Decimal 类型
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# 使用自定义编码器保存去重后的数据
try:
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(deduplicated_data, file, cls=DecimalEncoder, ensure_ascii=False, indent=2)
        print(f"成功保存去重后的 {len(deduplicated_data)} 条记录到 {output_file_path}")
except IOError as e:
    print(f"写入文件 {output_file_path} 时发生错误: {e}")

# 使用自定义编码器保存被去除的数据
try:
    with open(duplicates_file_path, 'w', encoding='utf-8') as file:
        json.dump(removed_duplicates, file, cls=DecimalEncoder, ensure_ascii=False, indent=2)
        print(f"成功保存 {len(removed_duplicates)} 条重复记录到 {duplicates_file_path}")
except IOError as e:
    print(f"写入文件 {duplicates_file_path} 时发生错误: {e}")

# 删除临时文件
import os
os.remove(temp_file_path)

print("所有操作已完成。")