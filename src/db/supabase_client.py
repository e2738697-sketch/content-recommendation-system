#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase 数据库客户端
提供数据库连接、查询、添加、更新操作
"""

import os
import json
from typing import Dict, List, Optional, Any
import logging

try:
    from supabase import create_client, Client
except ImportError:
    logging.warning("Supabase client not installed. Install with: pip install supabase")

logger = logging.getLogger(__name__)

class SupabaseClient:
    """
Supabase 数据库客户端包装器
    """
    
    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv("SUPABASE_URL", "")
        self.key = os.getenv("SUPABASE_KEY", "")
        
        if not self.url or not self.key:
            logger.warning("Supabase credentials not found in environment variables")
            self.client = None
            return
        
        try:
            self.client = create_client(self.url, self.key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            self.client = None
    
    def insert(self, table: str, data: Dict[str, Any]) -> Dict:
        """
        插入数据到表
        
        Args:
            table: 表名
            data: 数据字典
        
        Returns:
            插入的记录
        """
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            response = self.client.table(table).insert(data).execute()
            logger.info(f"Successfully inserted data into {table}")
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error inserting data into {table}: {str(e)}")
            raise
    
    def select(self, table: str, filters: Optional[Dict] = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        从表中查询数据
        
        Args:
            table: 表名
            filters: 筛选条件
            limit: 上限
            offset: 偏移
        
        Returns:
            查询结果列表
        """
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            query = self.client.table(table).select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.limit(limit).offset(offset).execute()
            logger.info(f"Successfully queried {len(response.data)} records from {table}")
            return response.data
        except Exception as e:
            logger.error(f"Error querying {table}: {str(e)}")
            raise
    
    def update(self, table: str, data: Dict[str, Any], condition_key: str, condition_value: Any) -> Dict:
        """
        更新表中的数据
        
        Args:
            table: 表名
            data: 要更新的数据
            condition_key: 条件字段
            condition_value: 条件值
        
        Returns:
            更新的记录
        """
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            response = self.client.table(table).update(data).eq(condition_key, condition_value).execute()
            logger.info(f"Successfully updated {table}")
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error updating {table}: {str(e)}")
            raise
    
    def delete(self, table: str, condition_key: str, condition_value: Any) -> None:
        """
        删除表中的数据
        
        Args:
            table: 表名
            condition_key: 条件字段
            condition_value: 条件值
        """
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            self.client.table(table).delete().eq(condition_key, condition_value).execute()
            logger.info(f"Successfully deleted record from {table}")
        except Exception as e:
            logger.error(f"Error deleting from {table}: {str(e)}")
            raise
    
    def count(self, table: str, filters: Optional[Dict] = None) -> int:
        """
        统计表中的记录数
        
        Args:
            table: 表名
            filters: 筛选条件
        
        Returns:
            记录总数
        """
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            query = self.client.table(table).select("count", count="exact")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.count
        except Exception as e:
            logger.error(f"Error counting records in {table}: {str(e)}")
            raise
    
    def batch_insert(self, table: str, data_list: List[Dict[str, Any]]) -> List[Dict]:
        """
        批量插入数据
        
        Args:
            table: 表名
            data_list: 数据列表
        
        Returns:
            插入的记录列表
        """
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            response = self.client.table(table).insert(data_list).execute()
            logger.info(f"Successfully batch inserted {len(response.data)} records into {table}")
            return response.data
        except Exception as e:
            logger.error(f"Error batch inserting into {table}: {str(e)}")
            raise


if __name__ == "__main__":
    # Test connection
    db = SupabaseClient()
    if db.client:
        print("Supabase connection successful!")
    else:
        print("Failed to connect to Supabase")
