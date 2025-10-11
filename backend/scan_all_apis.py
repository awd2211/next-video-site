#!/usr/bin/env python3
"""
快速扫描所有API端点并收集问题
"""
import sys
import asyncio
import requests
import re
from pathlib import Path
from collections import defaultdict

BASE_URL = "http://localhost:8000"

class APIScanner:
    def __init__(self):
        self.user_token = None
        self.admin_token = None
        self.issues = defaultdict(list)
        self.passed = []
        
    async def setup_auth(self):
        """设置认证"""
        print("设置认证tokens...")
        
        # 获取用户token
        try:
            resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "test123456"
            }, timeout=5)
            if resp.status_code == 200:
                self.user_token = resp.json()["access_token"]
                print(f"  ✓ 用户token获取成功")
        except Exception as e:
            print(f"  ✗ 用户token获取失败: {e}")
        
        # 获取管理员token
        try:
            from app.utils.cache import get_redis
            redis = await get_redis()
            
            cap_resp = requests.get(f"{BASE_URL}/api/v1/captcha/", timeout=5)
            cap_id = cap_resp.headers.get("x-captcha-id")
            cap_code = await redis.get(f"captcha:{cap_id}")
            
            resp = requests.post(f"{BASE_URL}/api/v1/auth/admin/login", json={
                "username": "admin",
                "password": "admin123456",
                "captcha_id": cap_id,
                "captcha_code": cap_code
            }, timeout=5)
            
            if resp.status_code == 200:
                self.admin_token = resp.json()["access_token"]
                print(f"  ✓ 管理员token获取成功\n")
            
            await redis.aclose()
        except Exception as e:
            print(f"  ✗ 管理员token获取失败: {e}\n")
    
    def extract_all_endpoints(self):
        """提取所有端点"""
        endpoints = []
        
        # API端点
        for f in Path("app/api").glob("*.py"):
            if f.name == "__init__.py":
                continue
            content = f.read_text()
            module = f.stem
            
            for method, path in re.findall(r'@router\.(get|post|put|delete|patch)\(["\']([^"\']*)["\']', content):
                full_path = f"/api/v1/{module}" + (path if path else "")
                full_path = full_path.replace("//", "/")
                endpoints.append((method.upper(), full_path, False, module))
        
        # Admin端点
        for f in Path("app/admin").glob("*.py"):
            if f.name == "__init__.py":
                continue
            content = f.read_text()
            module = f.stem
            
            for method, path in re.findall(r'@router\.(get|post|put|delete|patch)\(["\']([^"\']*)["\']', content):
                # 根据main.py的路由注册确定prefix
                if module in ["login", "logout", "me"]:
                    full_path = f"/api/v1/auth/admin/{module}" + (path if path else "")
                else:
                    prefix_map = {
                        "subtitles": "/api/v1/admin",
                        "transcode": "/api/v1/admin",
                        "settings": "/api/v1/admin/system",
                        "image_upload": "/api/v1/admin/images",
                    }
                    prefix = prefix_map.get(module, f"/api/v1/admin/{module}")
                    full_path = prefix + (path if path else "")
                
                full_path = full_path.replace("//", "/")
                endpoints.append((method.upper(), full_path, True, module))
        
        return endpoints
    
    def test_endpoint(self, method, path, is_admin, module):
        """测试单个端点"""
        # 跳过需要路径参数的
        if "{" in path:
            return "SKIP", "需要路径参数"
        
        url = BASE_URL + path
        headers = {}
        
        # 添加认证
        if is_admin and self.admin_token:
            headers["Authorization"] = f"Bearer {self.admin_token}"
        elif "/users/me" in path or "/favorites" in path or "/history" in path or "/notifications" in path:
            if self.user_token:
                headers["Authorization"] = f"Bearer {self.user_token}"
        
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, timeout=5)
            elif method == "POST":
                resp = requests.post(url, headers=headers, json={}, timeout=5)
            elif method == "PUT":
                resp = requests.put(url, headers=headers, json={}, timeout=5)
            elif method == "DELETE":
                resp = requests.delete(url, headers=headers, timeout=5)
            elif method == "PATCH":
                resp = requests.patch(url, headers=headers, json={}, timeout=5)
            else:
                return "SKIP", "未知方法"
            
            return resp.status_code, resp.text[:200] if resp.status_code >= 400 else ""
        except Exception as e:
            return "ERROR", str(e)[:100]
    
    async def run_scan(self):
        """运行扫描"""
        print("="*90)
        print("🔍 开始扫描所有API端点")
        print("="*90 + "\n")
        
        await self.setup_auth()
        
        endpoints = self.extract_all_endpoints()
        print(f"发现 {len(endpoints)} 个API端点\n")
        
        # 按模块分组测试
        by_module = defaultdict(list)
        for item in endpoints:
            by_module[item[3]].append(item)
        
        for module, eps in sorted(by_module.items()):
            print(f"\n{'='*90}")
            print(f"模块: {module} ({len(eps)} 个端点)")
            print(f"{'='*90}")
            
            for method, path, is_admin, _ in eps:
                status, msg = self.test_endpoint(method, path, is_admin, module)
                
                if status == "SKIP":
                    continue
                elif status == "ERROR":
                    print(f"  ✗ {method:6} {path:55} [ERROR: {msg}]")
                    self.issues["ERROR"].append((method, path, msg))
                elif status == 500:
                    print(f"  ✗ {method:6} {path:55} [500] {msg}")
                    self.issues["500_ERRORS"].append((method, path, msg))
                elif status == 401:
                    print(f"  ⚠ {method:6} {path:55} [401] 认证问题")
                    self.issues["AUTH_ISSUES"].append((method, path))
                elif status in [422, 400]:
                    print(f"  ⚠ {method:6} {path:55} [{status}] 参数问题")
                    self.issues["VALIDATION"].append((method, path))
                elif status in [200, 201, 204]:
                    print(f"  ✓ {method:6} {path:55} [{status}]")
                    self.passed.append((method, path))
                else:
                    print(f"  ? {method:6} {path:55} [{status}]")
                    self.issues["OTHER"].append((method, path, status))
        
        # 打印总结
        self.print_summary(len(endpoints))
        self.save_report()
    
    def print_summary(self, total):
        """打印总结"""
        print(f"\n{'='*90}")
        print("📊 扫描结果总结")
        print(f"{'='*90}\n")
        print(f"总端点数: {total}")
        print(f"✅ 通过: {len(self.passed)}")
        print(f"❌ 500错误: {len(self.issues['500_ERRORS'])}")
        print(f"⚠️  401认证问题: {len(self.issues['AUTH_ISSUES'])}")
        print(f"⚠️  422/400验证: {len(self.issues['VALIDATION'])}")
        print(f"❌ 连接错误: {len(self.issues['ERROR'])}")
        print(f"❓ 其他: {len(self.issues['OTHER'])}\n")
        
        if self.issues["500_ERRORS"]:
            print("【500 服务器错误 - 需要修复】:")
            for method, path, msg in self.issues["500_ERRORS"]:
                print(f"  • {method:6} {path}")
        
        if self.issues["AUTH_ISSUES"]:
            print(f"\n【401 认证问题 - 可能需要检查】: {len(self.issues['AUTH_ISSUES'])} 个")
    
    def save_report(self):
        """保存报告"""
        with open("API_TEST_ISSUES.md", "w") as f:
            f.write("# API测试问题报告\n\n")
            f.write(f"## 总结\n\n")
            f.write(f"- 总端点: {len(self.passed) + sum(len(v) for v in self.issues.values())}\n")
            f.write(f"- 通过: {len(self.passed)}\n")
            f.write(f"- 500错误: {len(self.issues['500_ERRORS'])}\n")
            f.write(f"- 认证问题: {len(self.issues['AUTH_ISSUES'])}\n\n")
            
            if self.issues["500_ERRORS"]:
                f.write("## 500错误（需要立即修复）\n\n")
                for method, path, msg in self.issues["500_ERRORS"]:
                    f.write(f"- `{method} {path}`\n")
                    f.write(f"  ```\n  {msg[:150]}\n  ```\n\n")
            
            if self.issues["AUTH_ISSUES"]:
                f.write("## 401认证问题\n\n")
                for method, path in self.issues["AUTH_ISSUES"][:20]:
                    f.write(f"- `{method} {path}`\n")
        
        print(f"\n报告已保存到: API_TEST_ISSUES.md\n")

async def main():
    scanner = APIScanner()
    await scanner.run_scan()

if __name__ == "__main__":
    asyncio.run(main())

