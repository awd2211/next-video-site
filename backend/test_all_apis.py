#!/usr/bin/env python3
"""
全面测试所有后端API端点
"""
import asyncio
import requests
import re
from pathlib import Path
from typing import Dict, List, Tuple
from app.utils.cache import get_redis

# 颜色
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.user_token = None
        self.admin_token = None
        self.results = {
            'passed': [],
            'failed': [],
            'skipped': [],
            'auth_required': []
        }
        
    async def get_user_token(self):
        """获取普通用户token"""
        try:
            response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "test123456"
            })
            if response.status_code == 200:
                self.user_token = response.json()['access_token']
                print(f"{GREEN}✓ 获取用户token成功{RESET}")
                return True
        except Exception as e:
            print(f"{RED}✗ 获取用户token失败: {e}{RESET}")
        return False
    
    async def get_admin_token(self):
        """获取管理员token"""
        try:
            redis = await get_redis()
            
            # 获取验证码
            cap_resp = requests.get(f"{BASE_URL}/api/v1/captcha/")
            cap_id = cap_resp.headers.get('x-captcha-id')
            cap_code = await redis.get(f'captcha:{cap_id}')
            
            # 登录
            response = requests.post(f"{BASE_URL}/api/v1/auth/admin/login", json={
                "username": "admin",
                "password": "admin123456",
                "captcha_id": cap_id,
                "captcha_code": cap_code
            })
            
            if response.status_code == 200:
                self.admin_token = response.json()['access_token']
                print(f"{GREEN}✓ 获取管理员token成功{RESET}")
                await redis.aclose()
                return True
            
            await redis.aclose()
        except Exception as e:
            print(f"{RED}✗ 获取管理员token失败: {e}{RESET}")
        return False
    
    def test_endpoint(self, method: str, path: str, is_admin: bool = False, 
                     requires_auth: bool = True, data: dict = None):
        """测试单个端点"""
        url = BASE_URL + path
        
        headers = {}
        if requires_auth:
            token = self.admin_token if is_admin else self.user_token
            if token:
                headers['Authorization'] = f'Bearer {token}'
            else:
                self.results['auth_required'].append((method, path))
                return None
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=5)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data or {}, timeout=5)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data or {}, timeout=5)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=5)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data or {}, timeout=5)
            else:
                return None
            
            return response.status_code
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def extract_endpoints(self):
        """提取所有后端端点"""
        endpoints = []
        
        # API端点
        for api_file in Path("app/api").glob("*.py"):
            if api_file.name == "__init__.py":
                continue
            
            content = api_file.read_text()
            module = api_file.stem
            
            pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']*)["\']'
            for method, route_path in re.findall(pattern, content):
                if route_path == "":
                    full_path = f"/api/v1/{module}"
                elif route_path.startswith("/"):
                    full_path = f"/api/v1/{module}{route_path}"
                else:
                    full_path = f"/api/v1/{module}/{route_path}"
                
                full_path = full_path.replace("//", "/")
                endpoints.append((method.upper(), full_path, False, module))
        
        # Admin端点
        for admin_file in Path("app/admin").glob("*.py"):
            if admin_file.name == "__init__.py":
                continue
            
            content = admin_file.read_text()
            module = admin_file.stem
            
            pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']*)["\']'
            for method, route_path in re.findall(pattern, content):
                # Admin路由的prefix在main.py中定义
                if route_path == "":
                    full_path = f"/api/v1/admin/{module}"
                elif route_path.startswith("/"):
                    full_path = f"/api/v1/admin/{module}{route_path}"
                else:
                    full_path = f"/api/v1/admin/{module}/{route_path}"
                
                full_path = full_path.replace("//", "/")
                # 修正特殊路由
                full_path = full_path.replace("/admin/login", "/auth/admin/login")
                full_path = full_path.replace("/admin/logout", "/auth/admin/logout")
                full_path = full_path.replace("/admin/me", "/auth/admin/me")
                
                endpoints.append((method.upper(), full_path, True, module))
        
        return endpoints
    
    def categorize_endpoint(self, method: str, path: str) -> str:
        """分类端点"""
        # 不需要认证的端点
        no_auth_patterns = [
            r'/api/v1/captcha',
            r'/api/v1/auth/login',
            r'/api/v1/auth/register',
            r'/api/v1/auth/refresh',
            r'/api/v1/videos/\d+$',
            r'/api/v1/videos$',
            r'/api/v1/videos/trending',
            r'/api/v1/videos/featured',
            r'/api/v1/videos/recommended',
            r'/api/v1/categories',
            r'/api/v1/countries',
            r'/api/v1/actors',
            r'/api/v1/directors',
            r'/api/v1/search',
        ]
        
        for pattern in no_auth_patterns:
            if re.match(pattern, path):
                return 'no_auth'
        
        # 需要参数的端点
        if '{' in path or ':param' in path:
            return 'needs_params'
        
        # 需要请求体的端点
        if method in ['POST', 'PUT', 'PATCH']:
            return 'needs_body'
        
        # 需要认证的端点
        if '/admin/' in path or '/me' in path or 'my-' in path:
            return 'needs_auth'
        
        return 'simple'
    
    async def run_tests(self):
        """运行所有测试"""
        print(f"\n{BLUE}{'='*90}{RESET}")
        print(f"{BLUE}🧪 全面API端点测试{RESET}")
        print(f"{BLUE}{'='*90}{RESET}\n")
        
        # 获取tokens
        print(f"{YELLOW}准备阶段：获取认证token...{RESET}")
        await self.get_user_token()
        await self.get_admin_token()
        
        # 提取所有端点
        endpoints = self.extract_endpoints()
        print(f"\n{BLUE}发现 {len(endpoints)} 个API端点{RESET}\n")
        
        # 分类测试
        categories = {
            'no_auth': [],
            'needs_params': [],
            'needs_body': [],
            'needs_auth': [],
            'simple': []
        }
        
        for method, path, is_admin, module in endpoints:
            category = self.categorize_endpoint(method, path)
            categories[category].append((method, path, is_admin, module))
        
        print(f"{YELLOW}端点分类：{RESET}")
        for cat, items in categories.items():
            print(f"  • {cat:15} {len(items):3} 个")
        
        # 测试不需要认证的端点
        print(f"\n{BLUE}{'='*90}{RESET}")
        print(f"{BLUE}测试公开API（无需认证）{RESET}")
        print(f"{BLUE}{'='*90}{RESET}\n")
        
        for method, path, is_admin, module in categories['no_auth'][:20]:  # 限制测试数量
            if '{' in path:
                # 跳过需要参数的
                continue
            
            status = self.test_endpoint(method, path, is_admin, requires_auth=False)
            
            if isinstance(status, int):
                if 200 <= status < 300:
                    print(f"{GREEN}✓{RESET} {method:6} {path:60} [{status}]")
                    self.results['passed'].append((method, path, status))
                elif status == 404 or status == 422:
                    print(f"{YELLOW}⚠{RESET} {method:6} {path:60} [{status}]")
                    self.results['skipped'].append((method, path, status))
                else:
                    print(f"{RED}✗{RESET} {method:6} {path:60} [{status}]")
                    self.results['failed'].append((method, path, status))
            else:
                print(f"{RED}✗{RESET} {method:6} {path:60} [{status}]")
                self.results['failed'].append((method, path, status))
        
        # 测试需要认证的简单端点
        print(f"\n{BLUE}{'='*90}{RESET}")
        print(f"{BLUE}测试需要认证的API{RESET}")
        print(f"{BLUE}{'='*90}{RESET}\n")
        
        auth_endpoints = [(m, p, ia, mod) for m, p, ia, mod in categories['simple'] 
                         if '/admin/' not in p and '{' not in p][:15]
        
        for method, path, is_admin, module in auth_endpoints:
            status = self.test_endpoint(method, path, is_admin, requires_auth=True)
            
            if isinstance(status, int):
                if 200 <= status < 300:
                    print(f"{GREEN}✓{RESET} {method:6} {path:60} [{status}]")
                    self.results['passed'].append((method, path, status))
                elif status == 404 or status == 422:
                    print(f"{YELLOW}⚠{RESET} {method:6} {path:60} [{status}]")
                    self.results['skipped'].append((method, path, status))
                else:
                    print(f"{RED}✗{RESET} {method:6} {path:60} [{status}]")
                    self.results['failed'].append((method, path, status))
        
        # 测试管理端点
        print(f"\n{BLUE}{'='*90}{RESET}")
        print(f"{BLUE}测试管理员API{RESET}")
        print(f"{BLUE}{'='*90}{RESET}\n")
        
        admin_endpoints = [(m, p, ia, mod) for m, p, ia, mod in endpoints 
                          if '/admin/' in p and '{' not in p and method == 'GET'][:20]
        
        for method, path, is_admin, module in admin_endpoints:
            status = self.test_endpoint(method, path, True, requires_auth=True)
            
            if isinstance(status, int):
                if 200 <= status < 300:
                    print(f"{GREEN}✓{RESET} {method:6} {path:60} [{status}]")
                    self.results['passed'].append((method, path, status))
                elif status == 404 or status == 422:
                    print(f"{YELLOW}⚠{RESET} {method:6} {path:60} [{status}]")
                    self.results['skipped'].append((method, path, status))
                else:
                    print(f"{RED}✗{RESET} {method:6} {path:60} [{status}]")
                    self.results['failed'].append((method, path, status))
        
        # 打印总结
        self.print_summary(len(endpoints))
    
    def print_summary(self, total_endpoints):
        """打印测试总结"""
        print(f"\n{BLUE}{'='*90}{RESET}")
        print(f"{BLUE}📊 测试结果总结{RESET}")
        print(f"{BLUE}{'='*90}{RESET}\n")
        
        tested = len(self.results['passed']) + len(self.results['failed']) + len(self.results['skipped'])
        
        print(f"总端点数: {total_endpoints}")
        print(f"已测试: {tested}")
        print(f"未测试: {total_endpoints - tested} (需要参数或复杂请求体)\n")
        
        print(f"{GREEN}✅ 通过: {len(self.results['passed'])}{RESET}")
        print(f"{YELLOW}⚠️  警告: {len(self.results['skipped'])}{RESET}")
        print(f"{RED}❌ 失败: {len(self.results['failed'])}{RESET}")
        
        if self.results['failed']:
            print(f"\n{RED}失败的端点：{RESET}")
            for method, path, status in self.results['failed'][:10]:
                print(f"  • {method:6} {path:60} [{status}]")
            if len(self.results['failed']) > 10:
                print(f"  ... 还有 {len(self.results['failed']) - 10} 个")
        
        if self.results['skipped']:
            print(f"\n{YELLOW}跳过的端点（需要特定参数）：{RESET}")
            for method, path, status in self.results['skipped'][:10]:
                print(f"  • {method:6} {path:60} [{status}]")
        
        print(f"\n{BLUE}{'='*90}{RESET}\n")
        
        # 计算通过率
        if tested > 0:
            pass_rate = (len(self.results['passed']) / tested) * 100
            print(f"通过率: {pass_rate:.1f}%")
            
            if pass_rate >= 90:
                print(f"{GREEN}✅ 测试结果优秀！{RESET}")
            elif pass_rate >= 70:
                print(f"{YELLOW}⚠️  部分端点需要检查{RESET}")
            else:
                print(f"{RED}❌ 发现较多问题，需要修复{RESET}")
        
        print()

async def main():
    tester = APITester()
    await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main())

