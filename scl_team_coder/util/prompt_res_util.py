import xml.etree.ElementTree as ET
import re
import json
from scl_team_coder import glovar

class PromptResultUtil():

    @classmethod
    def xml_to_dict(self, element):
        result = {}
        for child in element:
            if child:
                child_data = PromptResultUtil.xml_to_dict(child)
                if child.tag in result:
                    if isinstance(result[child.tag], list):
                        result[child.tag].append(child_data)
                    else:
                        result[child.tag] = [result[child.tag], child_data]
                else:
                    result[child.tag] = child_data
            else:
                result[child.tag] = child.text
        return result

    @classmethod
    def parse_xml(self, response: str) -> dict:
        if '```xml' in response:
            response = response.replace('```xml', '')
        if '```' in response:
            response = response.replace('```', '')

        try:
            root = ET.fromstring(response)
        except:
            try:
                root = ET.fromstring('<root>\n' + response + '\n</root>')
            except:
                root = ET.fromstring('<root>\n' + response)
        return PromptResultUtil.xml_to_dict(root)
    
    @classmethod
    def trim_text(self, text: str, trimmed_text: str):
        return text.replace(trimmed_text, '').strip()

    @classmethod
    def replace_tag(self, text: str, tag: str):
        return text.replace(f'<{tag}>', f'<{tag}><![CDATA[').replace(f'</{tag}>', f']]></{tag}>').strip()

    @classmethod
    def extract_xml_content(self, text: str) -> str:
        pattern = re.compile(r'<root>[\s\S]*?</root>')
        match = pattern.search(text)
        if match:
            return match.group(0)
        else:
            return ""
    
    @classmethod
    def get_json_content(self, name) -> str:
        with open(f"{glovar.RAG_DATA_DIR}/scl_case_code_modified/{name}.json", 'r', encoding='utf8') as f:
            code_json = f.read()
        return code_json

    @classmethod
    def get_source_code(self, name) -> str:
        with open(f"{glovar.RAG_DATA_DIR}/scl_case_code_modified/{name}.scl", 'r', encoding='utf8') as f:
            code_json = f.read()
        return code_json
