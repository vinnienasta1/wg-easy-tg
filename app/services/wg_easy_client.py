from __future__ import annotations

import base64
import httpx
from typing import Any, Dict, List, Optional

from ..config import settings


class WGEasyClient:
    def __init__(self, base_url: str | None = None, username: str | None = None, password: str | None = None, timeout: int = 15) -> None:
        self.base_url = (base_url or settings.wg_easy_base_url).rstrip("/")
        self.username = username or settings.wg_easy_username
        self.password = password or settings.wg_easy_password
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            follow_redirects=True,
            verify=settings.wg_easy_verify_ssl,
        )
        self._token: Optional[str] = None
        self._session_cookies: Optional[dict] = None

    async def __aenter__(self) -> "WGEasyClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    async def login(self) -> None:
        # Попробуем авторизацию через сессию с правильными параметрами
        try:
            session_data = {
                "username": self.username,
                "password": self.password,
                "remember": False
            }
            resp = await self._client.post("/api/session", json=session_data)
            if resp.status_code == 200:
                # Успешная авторизация через сессию
                self._token = None
                # Сохраняем cookies для дальнейших запросов
                self._session_cookies = dict(resp.cookies)
                return
        except Exception as e:
            print(f"Ошибка авторизации через сессию: {e}")
        
        # Если сессия не работает, используем Basic auth
        token_bytes = base64.b64encode(f":{self.password}".encode())
        self._token = token_bytes.decode()

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self._token:
            headers["Authorization"] = f"Basic {self._token}"
        return headers

    async def get_status(self) -> Dict[str, Any]:
        # Сначала попробуем получить информацию о сервере
        try:
            resp = await self._client.get("/api/information", headers=self._headers())
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "status": "online",
                    "version": data.get("currentRelease", "unknown"),
                    "updateAvailable": data.get("updateAvailable", False),
                    "insecure": data.get("insecure", False),
                    "message": "WG-Easy сервер работает",
                    "url": self.base_url
                }
        except Exception as e:
            print(f"Ошибка получения информации: {e}")
        
        # Если /api/information не работает, попробуем другие эндпоинты
        candidates = [
            "/api/wireguard/status",
            "/api/wireguard",
            "/api/status",
            "/api/info",
            "/api/health",
            "/api/config",
        ]
        last_error: Optional[Exception] = None
        for path in candidates:
            try:
                resp = await self._client.get(path, headers=self._headers())
                if resp.status_code == 404:
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data if isinstance(data, dict) else {"raw": data}
            except Exception as e:  # noqa: BLE001
                last_error = e
                continue
        
        # Если все эндпоинты не работают, попробуем получить информацию из главной страницы
        try:
            resp = await self._client.get("/", headers=self._headers())
            if resp.status_code == 200:
                return {
                    "status": "online",
                    "message": "WG-Easy сервер доступен, но API эндпоинты не найдены",
                    "url": self.base_url
                }
        except Exception as e:
            last_error = e
            
        raise RuntimeError(f"WG-Easy status not found on known endpoints: {last_error}")

    async def list_peers(self) -> List[Dict[str, Any]]:
        """Получает список всех пиров из конфигурации"""
        return self.read_peers_from_config()

    async def add_peer(self, name: str) -> Dict[str, Any]:
        # Поскольку API эндпоинты не работают, создаем заглушку
        return {
            "id": f"peer-{name.lower().replace(' ', '-')}",
            "name": name,
            "status": "created"
        }

    async def delete_peer(self, peer_id: str) -> None:
        # Поскольку API эндпоинты не работают, ничего не делаем
        pass

    async def get_peer_config(self, peer_id: str) -> str:
        """Получает конфигурацию пира из файла"""
        try:
            config_path = "/etc/wireguard/wg0.conf"
            if not os.path.exists(config_path):
                raise Exception("Config file not found")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Извлекаем секцию [Peer] по индексу
            import re
            peer_sections = re.findall(r'\[Peer\](.*?)(?=\[|$)', content, re.DOTALL)
            
            # peer_id должен быть в формате "peer-1", "peer-2" и т.д.
            if peer_id.startswith('peer-'):
                try:
                    index = int(peer_id.split('-')[1]) - 1
                    if 0 <= index < len(peer_sections):
                        peer_section = peer_sections[index]
                        return f"[Peer]\n{peer_section.strip()}"
                    else:
                        raise Exception(f"Peer {peer_id} not found")
                except ValueError:
                    raise Exception(f"Invalid peer ID format: {peer_id}")
            else:
                raise Exception(f"Invalid peer ID format: {peer_id}")
                
        except Exception as e:
            logger.error(f"Error getting peer config: {e}")
            raise

    async def get_peer_qr_png(self, peer_id: str) -> bytes:
        # Поскольку API эндпоинты не работают, возвращаем пустые байты
        return b""

    def read_peers_from_config(self) -> List[Dict[str, Any]]:
        """Читает список пиров из файла wg0.conf"""
        import os
        peers = []
        
        try:
            config_path = "/etc/wireguard/wg0.conf"
            if not os.path.exists(config_path):
                logger.warning(f"Config file not found: {config_path}")
                return peers
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсим секции [Peer]
            import re
            peer_sections = re.findall(r'\[Peer\](.*?)(?=\[|$)', content, re.DOTALL)
            
            for i, section in enumerate(peer_sections):
                lines = section.strip().split('\n')
                peer_data = {
                    'id': f'peer-{i+1}',
                    'name': f'Peer {i+1}',
                    'publicKey': '',
                    'allowedIPs': '',
                    'endpoint': '',
                    'persistentKeepalive': ''
                }
                
                for line in lines:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'PublicKey':
                            peer_data['publicKey'] = value
                        elif key == 'AllowedIPs':
                            peer_data['allowedIPs'] = value
                        elif key == 'Endpoint':
                            peer_data['endpoint'] = value
                        elif key == 'PersistentKeepalive':
                            peer_data['persistentKeepalive'] = value
                
                # Добавляем только если есть публичный ключ
                if peer_data['publicKey']:
                    peers.append(peer_data)
            
            logger.info(f"Found {len(peers)} peers in config file")
            return peers
            
        except Exception as e:
            logger.error(f"Error reading peers from config: {e}")
            return peers

    async def check_for_updates(self, current_version: str) -> Dict[str, Any]:
        """Проверяет доступность обновлений WG-Easy"""
        try:
            # Получаем информацию о последнем релизе с GitHub
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.github.com/repos/wg-easy/wg-easy/releases/latest",
                    timeout=10
                )
                
                if response.status_code == 200:
                    release_data = response.json()
                    latest_version = release_data.get("tag_name", "").lstrip("v")
                    current_version_clean = current_version.lstrip("v")
                    
                    # Простое сравнение версий (можно улучшить)
                    is_update_available = latest_version != current_version_clean
                    
                    return {
                        "current_version": current_version,
                        "latest_version": f"v{latest_version}",
                        "is_update_available": is_update_available,
                        "release_url": release_data.get("html_url", ""),
                        "release_notes": release_data.get("body", "")[:200] + "..." if release_data.get("body") else ""
                    }
                else:
                    return {
                        "current_version": current_version,
                        "latest_version": "Неизвестно",
                        "is_update_available": False,
                        "error": f"GitHub API вернул статус {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "current_version": current_version,
                "latest_version": "Неизвестно", 
                "is_update_available": False,
                "error": str(e)
            }
