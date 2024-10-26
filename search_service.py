import requests
from typing import List, Dict, Any
import json

class SearchService:
    """搜索服务类，用于获取网络搜索结果"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        执行搜索并返回结果
        
        Args:
            query: 搜索查询
            limit: 返回结果数量限制
            
        Returns:
            搜索结果列表
        """
        try:
            payload = {
                "q": query,
                "gl": "cn",  # 地理位置设置为中国
                "hl": "zh-cn"  # 语言设置为中文
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            results = response.json()
            organic_results = results.get('organic', [])[:limit]
            
            formatted_results = []
            for result in organic_results:
                formatted_results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'link': result.get('link', '')
                })
                
            return formatted_results
            
        except Exception as e:
            print(f"搜索出错: {str(e)}")
            return []
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        将搜索结果格式化为文本
        
        Args:
            results: 搜索结果列表
            
        Returns:
            格式化后的文本
        """
        if not results:
            return "未找到相关搜索结果。"
            
        formatted_text = "搜索结果参考信息：\n\n"
        for i, result in enumerate(results, 1):
            formatted_text += f"{i}. {result['title']}\n"
            formatted_text += f"摘要: {result['snippet']}\n"
            formatted_text += f"来源: {result['link']}\n\n"
            
        return formatted_text
