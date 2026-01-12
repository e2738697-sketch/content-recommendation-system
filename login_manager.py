#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录管理器
管理小红书和抖音的登录状态
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

class LoginManager:
    """登录管理器"""
    
    def __init__(self):
        self.login_dir = Path("data/logins")
        self.login_dir.mkdir(parents=True, exist_ok=True)
        
        # 登录状态文件
        self.xhs_login_file = self.login_dir / "xhs_login.json"
        self.douyin_login_file = self.login_dir / "douyin_login.json"
    
    def get_login_status(self, platform: str) -> Dict:
        """获取登录状态"""
        login_file = self.xhs_login_file if platform == "xhs" else self.douyin_login_file
        
        if login_file.exists():
            try:
                with open(login_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "logged_in": False,
            "login_time": None,
            "cookies": None,
            "user_info": None
        }
    
    def save_login_status(self, platform: str, cookies: Dict, user_info: Dict = None):
        """保存登录状态"""
        login_file = self.xhs_login_file if platform == "xhs" else self.douyin_login_file
        
        status = {
            "logged_in": True,
            "login_time": datetime.now().isoformat(),
            "cookies": cookies,
            "user_info": user_info or {}
        }
        
        with open(login_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {platform} 登录状态已保存")
    
    def clear_login_status(self, platform: str):
        """清除登录状态"""
        login_file = self.xhs_login_file if platform == "xhs" else self.douyin_login_file
        
        if login_file.exists():
            login_file.unlink()
            print(f"✅ {platform} 登录状态已清除")
    
    def get_cookies_for_platform(self, platform: str) -> Optional[Dict]:
        """获取平台的cookies"""
        status = self.get_login_status(platform)
        if status.get("logged_in") and status.get("cookies"):
            return status["cookies"]
        return None
