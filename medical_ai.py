from abc import ABC, abstractmethod
import openai
from typing import Optional, Dict, Any, List
import os
from openai import OpenAI
from prompts import MEDICAL_ADVICE_PROMPT
from search_service import SearchService

class AIProvider(ABC):
    """AI服务提供者的抽象基类"""
    
    @abstractmethod
    def generate_response(self, prompt: str, conversation_history: Optional[List] = None) -> str:
        """生成AI回复的抽象方法"""
        pass

class DeepSeekProvider(AIProvider):
    """DeepSeek服务实现，支持多轮对话"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key is required")
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        self.conversation_history = []

    def generate_response(self, prompt: str, conversation_history: Optional[List] = None) -> str:
        try:
            # 如果提供了外部对话历史，使用它；否则使用内部历史
            messages = conversation_history if conversation_history is not None else self.conversation_history
            
            # 如果是新对话，添加系统提示
            if not messages:
                messages = [{"role": "system", "content": MEDICAL_ADVICE_PROMPT}]
            
            # 添加用户的新问题
            messages.append({"role": "user", "content": prompt})
            
            # 调用API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.7,  # 添加温度参数以控制回答的创造性
                max_tokens=400,   # 限制回答长度
                stream=False
            )
            
            # 保存AI的回复到对话历史
            ai_message = response.choices[0].message
            messages.append({"role": ai_message.role, "content": ai_message.content})
            
            # 更新内部对话历史
            if conversation_history is None:
                self.conversation_history = messages
            
            return ai_message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []

class MedicalAI:
    """医疗AI服务的主类"""
    
    def __init__(self, provider: AIProvider, search_service: Optional[SearchService] = None):
        self.provider = provider
        self.search_service = search_service
        self.conversation_history = []

    def should_use_search(self, prompt: str) -> bool:
        """判断是否需要使用搜索功能"""
        # 包含特定关键词的问题可能需要最新信息
        search_keywords = [
            "最新", "研究", "进展", "新闻", "最近",
            "数据", "统计", "报告", "新型", "新药",
            "临床试验", "治疗方法"
        ]
        
        return any(keyword in prompt for keyword in search_keywords)

    def get_medical_advice(self, prompt: str) -> str:
        """获取医疗建议"""
        if not prompt.strip().endswith(('。', '？', '！', '.', '?', '!')):
            prompt = prompt.strip() + '。'
        
        # 添加调试信息
        should_search = self.should_use_search(prompt)
        print(f"问题包含搜索关键词: {should_search}")
        print(f"搜索服务是否可用: {self.search_service is not None}")
        
        search_context = ""
        reference_links = []
        
        if self.search_service and should_search:
            print("正在执行搜索...")
            search_results = self.search_service.search(prompt)
            if search_results:
                print(f"找到 {len(search_results)} 条搜索结果")
                search_context = self.search_service.format_search_results(search_results)
                reference_links = [result['link'] for result in search_results]
            else:
                print("未找到搜索结果")
        
        # 将搜索结果作为上下文添加到提示中
        if search_context:
            enhanced_prompt = f"{search_context}\n\n基于以上参考信息，请回答以下问题。在回答的最后，请列出参考来源：\n{prompt}"
        else:
            enhanced_prompt = prompt
            
        response = self.provider.generate_response(enhanced_prompt, self.conversation_history)
        
        # 如果有搜索结果，在回答末尾添加参考链接
        if reference_links:
            response += "\n\n参考来源：\n"
            for i, link in enumerate(reference_links, 1):
                response += f"{i}. {link}\n"
            
        return response
    
    def clear_conversation(self):
        """清除当前对话历史"""
        self.conversation_history = []
        if hasattr(self.provider, 'clear_history'):
            self.provider.clear_history()

def create_medical_ai(
    provider_type: str = "deepseek",
    enable_search: bool = False,
    serper_api_key: Optional[str] = None,
    **kwargs
) -> MedicalAI:
    """
    工厂函数，创建MedicalAI实例
    
    Args:
        provider_type: AI提供者类型 ("deepseek")
        enable_search: 是否启用搜索功能
        serper_api_key: Serper API密钥
        **kwargs: 提供者特定的配置参数
    """
    providers = {
        "deepseek": lambda: DeepSeekProvider(**kwargs)
    }
    
    if provider_type not in providers:
        raise ValueError(f"Unsupported provider type: {provider_type}")
    
    search_service = None
    if enable_search:
        if not serper_api_key:
            raise ValueError("Serper API key is required when search is enabled")
        search_service = SearchService(serper_api_key)
    
    return MedicalAI(providers[provider_type](), search_service)
