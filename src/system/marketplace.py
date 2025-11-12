from typing import Dict, Any, Optional, List
import aiohttp
import logging
from pathlib import Path
import json
import hashlib
import zipfile
import shutil
import asyncio
from datetime import datetime

class PluginMarketplace:
    """Система управления маркетплейсом плагинов."""
    
    def __init__(self, 
                 marketplace_url: str,
                 plugins_dir: Path,
                 cache_dir: Path):
        self.marketplace_url = marketplace_url
        self.plugins_dir = plugins_dir
        self.cache_dir = cache_dir
        self.logger = logging.getLogger(__name__)
        
        # Создаем необходимые директории
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    async def get_plugin_catalog(self) -> List[Dict[str, Any]]:
        """Получает каталог доступных плагинов."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.marketplace_url}/plugins") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Failed to get plugin catalog: {response.status}")
                        return []
            except Exception as e:
                self.logger.error(f"Error getting plugin catalog: {e}")
                return []
                
    async def search_plugins(self, 
                           query: str,
                           category: Optional[str] = None,
                           sort_by: str = "downloads") -> List[Dict[str, Any]]:
        """Поиск плагинов в маркетплейсе.
        
        Args:
            query: Поисковый запрос
            category: Категория плагинов
            sort_by: Поле для сортировки (downloads, rating, date)
            
        Returns:
            Список найденных плагинов
        """
        params = {
            "q": query,
            "sort": sort_by
        }
        if category:
            params["category"] = category
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.marketplace_url}/search",
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Search failed: {response.status}")
                        return []
            except Exception as e:
                self.logger.error(f"Error searching plugins: {e}")
                return []
                
    async def get_plugin_details(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Получает детальную информацию о плагине."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.marketplace_url}/plugins/{plugin_id}"
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Failed to get plugin details: {response.status}")
                        return None
            except Exception as e:
                self.logger.error(f"Error getting plugin details: {e}")
                return None
                
    async def download_plugin(self, 
                            plugin_id: str,
                            version: Optional[str] = None) -> Optional[Path]:
        """Загружает плагин из маркетплейса.
        
        Args:
            plugin_id: ID плагина
            version: Версия плагина (None для последней версии)
            
        Returns:
            Путь к загруженному архиву или None при ошибке
        """
        url = f"{self.marketplace_url}/plugins/{plugin_id}/download"
        if version:
            url += f"?version={version}"
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        # Получаем имя файла из заголовка
                        filename = response.headers.get(
                            "content-disposition",
                            f"filename={plugin_id}.zip"
                        ).split("filename=")[-1]
                        
                        # Сохраняем файл
                        file_path = self.cache_dir / filename
                        with open(file_path, 'wb') as f:
                            while True:
                                chunk = await response.content.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                                
                        return file_path
                    else:
                        self.logger.error(f"Download failed: {response.status}")
                        return None
            except Exception as e:
                self.logger.error(f"Error downloading plugin: {e}")
                return None
                
    async def install_plugin(self,
                           plugin_id: str,
                           version: Optional[str] = None) -> bool:
        """Устанавливает плагин из маркетплейса.
        
        Args:
            plugin_id: ID плагина
            version: Версия плагина (None для последней версии)
            
        Returns:
            True если установка успешна
        """
        # Загружаем плагин
        archive_path = await self.download_plugin(plugin_id, version)
        if not archive_path:
            return False
            
        try:
            # Создаем директорию для плагина
            plugin_dir = self.plugins_dir / plugin_id
            plugin_dir.mkdir(parents=True, exist_ok=True)
            
            # Распаковываем архив
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(plugin_dir)
                
            # Проверяем структуру плагина
            manifest_path = plugin_dir / "manifest.json"
            if not manifest_path.exists():
                self.logger.error(f"Invalid plugin structure: no manifest.json")
                shutil.rmtree(plugin_dir)
                return False
                
            # Проверяем версию
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                
            if version and manifest.get("version") != version:
                self.logger.error(f"Version mismatch: {manifest.get('version')} != {version}")
                shutil.rmtree(plugin_dir)
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing plugin: {e}")
            if plugin_dir.exists():
                shutil.rmtree(plugin_dir)
            return False
        finally:
            # Очищаем кэш
            archive_path.unlink()
            
    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """Удаляет установленный плагин."""
        plugin_dir = self.plugins_dir / plugin_id
        
        if not plugin_dir.exists():
            return False
            
        try:
            shutil.rmtree(plugin_dir)
            return True
        except Exception as e:
            self.logger.error(f"Error uninstalling plugin: {e}")
            return False
            
    async def update_plugin(self,
                          plugin_id: str,
                          target_version: Optional[str] = None) -> bool:
        """Обновляет плагин до указанной или последней версии."""
        # Проверяем текущую версию
        current_manifest_path = self.plugins_dir / plugin_id / "manifest.json"
        if not current_manifest_path.exists():
            return False
            
        with open(current_manifest_path, 'r') as f:
            current_manifest = json.load(f)
            
        current_version = current_manifest.get("version")
        
        # Получаем информацию о последней версии
        plugin_info = await self.get_plugin_details(plugin_id)
        if not plugin_info:
            return False
            
        latest_version = plugin_info.get("latest_version")
        if not latest_version:
            return False
            
        # Определяем целевую версию
        version_to_install = target_version or latest_version
        
        # Проверяем необходимость обновления
        if current_version == version_to_install:
            return True
            
        # Удаляем текущую версию
        if not await self.uninstall_plugin(plugin_id):
            return False
            
        # Устанавливаем новую версию
        return await self.install_plugin(plugin_id, version_to_install)
        
    def get_installed_plugins(self) -> List[Dict[str, Any]]:
        """Возвращает список установленных плагинов."""
        installed = []
        
        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
                
            manifest_path = plugin_dir / "manifest.json"
            if not manifest_path.exists():
                continue
                
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    installed.append(manifest)
            except Exception as e:
                self.logger.error(f"Error reading manifest for {plugin_dir}: {e}")
                
        return installed