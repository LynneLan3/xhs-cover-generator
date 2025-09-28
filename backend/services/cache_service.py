import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional


class CacheService:
    def __init__(self, cache_dir: str = "cache", cache_ttl: int = 3600 * 24):
        """
        初始化缓存服务
        
        Args:
            cache_dir: 缓存目录路径
            cache_ttl: 缓存过期时间（秒），默认24小时
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_ttl = cache_ttl
    
    def _generate_cache_key(self, title: str, author: str, style_id: str) -> str:
        """
        基于标题、作者和风格ID生成缓存键
        
        Args:
            title: 标题
            author: 作者
            style_id: 风格ID
            
        Returns:
            缓存键的MD5哈希值
        """
        # 将输入参数组合成字符串，然后生成MD5哈希
        cache_input = f"{title}|{author or ''}|{style_id}"
        return hashlib.md5(cache_input.encode('utf-8')).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, title: str, author: str, style_id: str) -> Optional[str]:
        """
        从缓存中获取HTML内容
        
        Args:
            title: 标题
            author: 作者
            style_id: 风格ID
            
        Returns:
            缓存的HTML内容，如果不存在或已过期则返回None
        """
        cache_key = self._generate_cache_key(title, author, style_id)
        cache_file = self._get_cache_file_path(cache_key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查是否过期
            if time.time() - cache_data['timestamp'] > self.cache_ttl:
                # 删除过期缓存
                cache_file.unlink()
                return None
            
            return cache_data['html']
        except (json.JSONDecodeError, KeyError, OSError):
            # 缓存文件损坏，删除它
            if cache_file.exists():
                cache_file.unlink()
            return None
    
    def set(self, title: str, author: str, style_id: str, html: str) -> None:
        """
        将HTML内容存储到缓存
        
        Args:
            title: 标题
            author: 作者
            style_id: 风格ID
            html: 要缓存的HTML内容
        """
        cache_key = self._generate_cache_key(title, author, style_id)
        cache_file = self._get_cache_file_path(cache_key)
        
        cache_data = {
            'timestamp': time.time(),
            'title': title,
            'author': author or '',
            'style_id': style_id,
            'html': html
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            # 写入失败，记录错误但不影响主流程
            print(f"缓存写入失败: {e}")
    
    def clear_expired(self) -> int:
        """
        清理过期的缓存文件
        
        Returns:
            清理的文件数量
        """
        cleared_count = 0
        current_time = time.time()
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if current_time - cache_data['timestamp'] > self.cache_ttl:
                    cache_file.unlink()
                    cleared_count += 1
            except (json.JSONDecodeError, KeyError, OSError):
                # 损坏的缓存文件也删除
                cache_file.unlink()
                cleared_count += 1
        
        return cleared_count
    
    def clear_all(self) -> int:
        """
        清理所有缓存文件
        
        Returns:
            清理的文件数量
        """
        cleared_count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                cleared_count += 1
            except OSError:
                pass
        
        return cleared_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            包含缓存统计信息的字典
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_files = len(cache_files)
        valid_files = 0
        expired_files = 0
        corrupted_files = 0
        current_time = time.time()
        
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if current_time - cache_data['timestamp'] > self.cache_ttl:
                    expired_files += 1
                else:
                    valid_files += 1
            except (json.JSONDecodeError, KeyError, OSError):
                corrupted_files += 1
        
        return {
            'total_files': total_files,
            'valid_files': valid_files,
            'expired_files': expired_files,
            'corrupted_files': corrupted_files,
            'cache_dir': str(self.cache_dir),
            'cache_ttl': self.cache_ttl
        }


# 全局缓存实例
cache_service = CacheService()