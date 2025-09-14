"""
飞书多维表格完整集成模块
实现多维表格的自动创建、管理和双向同步
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from utils.logger import get_logger
from utils.date_utils import DateUtils


class FeishuBitableManager:
    """飞书多维表格管理器"""
    
    def __init__(self, app_id: str, app_secret: str, base_url: str = "https://open.feishu.cn/open-apis"):
        self.logger = get_logger("feishu_bitable")
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url
        
        # 访问令牌
        self.access_token = None
        self.token_expires = None
        
        # 表格管理
        self.app_token = None
        self.tables = {}
        
        # 初始化
        self.date_utils = DateUtils()
    
    def get_access_token(self) -> Optional[str]:
        """获取飞书访问令牌"""
        try:
            if self.access_token and self.token_expires:
                if datetime.now() < self.token_expires:
                    return self.access_token
            
            # 获取新的访问令牌
            url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
            
            headers = {
                "Content-Type": "application/json; charset=utf-8"
            }
            
            data = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"飞书API响应: {result}")
                if result.get("code") == 0:
                    self.access_token = result.get("tenant_access_token")
                    expires_in = result.get("expire", 3600)
                    self.token_expires = datetime.now() + timedelta(seconds=expires_in - 300)
                    
                    self.logger.info("飞书访问令牌获取成功")
                    return self.access_token
                else:
                    self.logger.error(f"获取访问令牌失败: {result.get('msg', 'Unknown error')}")
                    self.logger.error(f"错误代码: {result.get('code')}")
                    return None
            else:
                self.logger.error(f"获取访问令牌失败: {response.status_code}")
                self.logger.error(f"响应内容: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取访问令牌失败: {e}")
            return None
    
    def create_app(self, app_name: str = "股票投资分析管理系统") -> Optional[str]:
        """创建飞书应用"""
        try:
            token = self.get_access_token()
            if not token:
                return None
            
            url = f"{self.base_url}/bitable/v1/apps"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "app_token": "",
                "name": app_name,
                "description": "股票投资分析管理系统的多维表格"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    app_token = result.get("data", {}).get("app", {}).get("app_token")
                    self.app_token = app_token
                    self.logger.info(f"飞书应用创建成功: {app_token}")
                    return app_token
                else:
                    self.logger.error(f"创建应用失败: {result.get('msg')}")
                    return None
            else:
                self.logger.error(f"创建应用失败: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"创建应用失败: {e}")
            return None
    
    def create_table(self, table_name: str, fields: List[Dict]) -> Optional[str]:
        """创建多维表格"""
        try:
            token = self.get_access_token()
            if not token or not self.app_token:
                return None
            
            url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # 尝试更简单的字段格式
            simplified_fields = []
            for i, field in enumerate(fields):
                field_name = field.get("field_name", field.get("name", f"field_{i}"))
                simplified_fields.append({
                    "field_name": field_name,
                    "type": "text"
                })
            
            # 尝试最简单的数据结构
            data = {
                "name": table_name,
                "fields": simplified_fields
            }
            
            self.logger.info(f"创建表格请求: {json.dumps(data, ensure_ascii=False)}")
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"创建表格响应: {json.dumps(result, ensure_ascii=False)}")
                
                if result.get("code") == 0:
                    table_id = result.get("data", {}).get("table", {}).get("table_id")
                    if not table_id:
                        # 尝试从不同的路径获取table_id
                        table_id = result.get("data", {}).get("table_id")
                    self.tables[table_name] = table_id
                    self.logger.info(f"表格创建成功: {table_name} -> {table_id}")
                    return table_id
                else:
                    self.logger.error(f"创建表格失败: {result.get('msg')}")
                    self.logger.error(f"错误代码: {result.get('code')}")
                    self.logger.error(f"完整响应: {json.dumps(result, ensure_ascii=False)}")
                    return None
            else:
                self.logger.error(f"创建表格失败: {response.status_code}")
                self.logger.error(f"响应内容: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"创建表格失败: {e}")
            return None
    
    def add_record(self, table_name: str, record_data: Dict) -> Dict:
        """添加记录到表格"""
        try:
            token = self.get_access_token()
            if not token or not self.app_token:
                return {'success': False, 'error': 'Token or app_token not available'}
            
            table_id = self.tables.get(table_name)
            if not table_id:
                return {'success': False, 'error': f'Table {table_name} not found'}
            
            url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{table_id}/records"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "fields": record_data
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    record_id = result.get("data", {}).get("record", {}).get("record_id")
                    self.logger.info(f"记录添加成功: {table_name} -> {record_id}")
                    return {'success': True, 'record_id': record_id}
                else:
                    self.logger.error(f"添加记录失败: {result.get('msg')}")
                    return {'success': False, 'error': result.get('msg')}
            else:
                self.logger.error(f"添加记录失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            self.logger.error(f"添加记录失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_records(self, table_name: str, limit: int = 100) -> List[Dict]:
        """获取表格记录"""
        try:
            token = self.get_access_token()
            if not token or not self.app_token:
                return []
            
            table_id = self.tables.get(table_name)
            if not table_id:
                return []
            
            url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{table_id}/records"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "page_size": limit
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    records = result.get("data", {}).get("items", [])
                    return records
                else:
                    self.logger.error(f"获取记录失败: {result.get('msg')}")
                    return []
            else:
                self.logger.error(f"获取记录失败: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"获取记录失败: {e}")
            return []
    
    def update_record(self, table_name: str, record_id: str, update_data: Dict) -> Dict:
        """更新记录"""
        try:
            token = self.get_access_token()
            if not token or not self.app_token:
                return {'success': False, 'error': 'Token or app_token not available'}
            
            table_id = self.tables.get(table_name)
            if not table_id:
                return {'success': False, 'error': f'Table {table_name} not found'}
            
            url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "fields": update_data
            }
            
            response = requests.put(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    self.logger.info(f"记录更新成功: {table_name} -> {record_id}")
                    return {'success': True}
                else:
                    self.logger.error(f"更新记录失败: {result.get('msg')}")
                    return {'success': False, 'error': result.get('msg')}
            else:
                self.logger.error(f"更新记录失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            self.logger.error(f"更新记录失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_record(self, table_name: str, record_id: str) -> Dict:
        """删除记录"""
        try:
            token = self.get_access_token()
            if not token or not self.app_token:
                return {'success': False, 'error': 'Token or app_token not available'}
            
            table_id = self.tables.get(table_name)
            if not table_id:
                return {'success': False, 'error': f'Table {table_name} not found'}
            
            url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.delete(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    self.logger.info(f"记录删除成功: {table_name} -> {record_id}")
                    return {'success': True}
                else:
                    self.logger.error(f"删除记录失败: {result.get('msg')}")
                    return {'success': False, 'error': result.get('msg')}
            else:
                self.logger.error(f"删除记录失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            self.logger.error(f"删除记录失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_table_share_link(self, table_name: str) -> Optional[str]:
        """获取表格分享链接"""
        try:
            token = self.get_access_token()
            if not token or not self.app_token:
                return None
            
            table_id = self.tables.get(table_name)
            if not table_id:
                return None
            
            url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{table_id}/share"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "type": "read_only",
                "expire_time": "never"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    share_url = result.get("data", {}).get("url")
                    self.logger.info(f"表格分享链接生成成功: {share_url}")
                    return share_url
                else:
                    self.logger.error(f"生成分享链接失败: {result.get('msg')}")
                    return None
            else:
                self.logger.error(f"生成分享链接失败: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"生成分享链接失败: {e}")
            return None