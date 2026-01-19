#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI标注引擎
使用自然语言处理模型进行内容多维度标注
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class TaggingEngine:
    """
    AI标注引擎 - 支持多维度内容标注
    
    标注维度:
    - 品类 (category): 护肆、化妆、服饰、运动等
    - 价格带 (price_band): <100, 100-300, 300-800, 800+
    - 场景 (scenario): 上男、居家、约会、旅游等
    - 风格 (style): 种草、测评、晰单、开箱、踏雷
    - 情绪分 (sentiment_score): -1.0~1.0
    """
    
    def __init__(self):
        """Initialize tagging engine"""
        self.categories = [
            '护肆', '化妆', '底妆', '香水', '香纸',
            '服饰', '鞋类', '布薄', '篥子',
            '运动', '健身', '瞬顿', '旅游',
            '美食', '饮品', '家居', '数码'
        ]
        
        self.price_bands = ['<100', '100-300', '300-800', '800+']
        
        self.scenarios = [
            '通勤', '居家', '上班', '约会', 
            '旅游', '运动', '贵族', '日常'
        ]
        
        self.styles = [
            '种草', '测评', '晰单', '开箱', 
            '踏雷', '教程', '同欺', '林雊'
        ]
        
        logger.info("TaggingEngine initialized")
    
    def tag(self, title: str, description: Optional[str] = None, 
            hashtags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        对内容进行多维度标注
        
        Args:
            title: 内容标题
            description: 内容描述
            hashtags: 品算标签
        
        Returns:
            标注结果
        """
        try:
            # 结合所有文本
            full_text = title.lower()
            if description:
                full_text += " " + description.lower()
            if hashtags:
                full_text += " " + " ".join(hashtags).lower()
            
            # 1. 推断品类
            category = self._infer_category(full_text)
            
            # 2. 推断价格带
            price_band = self._infer_price_band(full_text)
            
            # 3. 推断场景
            scenarios = self._infer_scenarios(full_text)
            
            # 4. 推断风格
            style = self._infer_style(full_text)
            
            # 5. 计算情绪分
            sentiment_score = self._calculate_sentiment(full_text)
            
            result = {
                "category": category,
                "price_band": price_band,
                "scenarios": scenarios,
                "style": style,
                "sentiment_score": sentiment_score,
                "tagged_at": datetime.now().isoformat()
            }
            
            logger.info(f"Tagged content: {result}")
            return result
        except Exception as e:
            logger.error(f"Error tagging content: {str(e)}")
            return {"error": str(e)}
    
    def _infer_category(self, text: str) -> str:
        """推断品类"""
        keywords = {
            '护肆': ['居宝室', '面腫', '面膜', '沛', '抗氧'],
            '化妆': ['笔', '沛', '粗', '细'],
            '服饰': ['衣', '裳', '裙', '上衣'],
            '运动': ['靠', '網', '跫', '较动'],
            '美食': ['食', '似', '饮'],
        }
        
        scores = {cat: 0 for cat in self.categories}
        for category, kws in keywords.items():
            for kw in kws:
                scores[category] += text.count(kw)
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else '其他'
    
    def _infer_price_band(self, text: str) -> str:
        """推断价格带"""
        high_price_keywords = ['奖', '建议', '值', '元']
        medium_price_keywords = ['经济', '宜']
        low_price_keywords = ['便宜', '广', '便']
        
        high_count = sum(text.count(kw) for kw in high_price_keywords)
        medium_count = sum(text.count(kw) for kw in medium_price_keywords)
        low_count = sum(text.count(kw) for kw in low_price_keywords)
        
        if high_count > 0:
            return '800+' if high_count > 2 else '300-800'
        elif medium_count > 0:
            return '100-300'
        elif low_count > 0:
            return '<100'
        else:
            return '100-300'  # 默认值
    
    def _infer_scenarios(self, text: str) -> List[str]:
        """推断场景"""
        scenario_keywords = {
            '通勤': ['上班', '换乘', '地铁'],
            '居家': ['居', '家', '休関'],
            '约会': ['约', '会', '猴'],
            '旅游': ['旅', '游', '外出'],
        }
        
        detected = []
        for scenario, kws in scenario_keywords.items():
            if any(kw in text for kw in kws):
                detected.append(scenario)
        
        return detected if detected else ['日常']
    
    def _infer_style(self, text: str) -> str:
        """推断风格"""
        style_keywords = {
            '种草': ['亲测', '牢贫', '感受'],
            '测评': ['测', '试', '每'],
            '晰单': ['写真', '晰', '单'],
            '开箱': ['上拨', '算是', '拨'],
            '踏雷': ['不推', '弃', '清洗'],
        }
        
        scores = {style: 0 for style in self.styles}
        for style, kws in style_keywords.items():
            for kw in kws:
                scores[style] += text.count(kw)
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else '教程'
    
    def _calculate_sentiment(self, text: str) -> float:
        """计算情绪分整体横或纵候"""
        positive_words = ['不错', '好', '爱', '旅游', '牡輪', '推荐']
        negative_words = ['不好', '不嘛', '不妭', '府一惊', '踏雷']
        
        positive_count = sum(text.count(word) for word in positive_words)
        negative_count = sum(text.count(word) for word in negative_words)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.5  # 中立
        
        sentiment = (positive_count - negative_count) / total
        return max(-1.0, min(1.0, sentiment))


if __name__ == "__main__":
    engine = TaggingEngine()
    
    # 测试示例
    test_title = "护肆测评：【客休】推荐大甜水业加辕面腫沛"
    result = engine.tag(test_title)
    print(json.dumps(result, ensure_ascii=False, indent=2))
