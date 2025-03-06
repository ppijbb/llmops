import json
import logging
import uuid
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Scope, Receive, Send, Message
from starlette.responses import RedirectResponse
import aiohttp

from app.logger import get_logger

class OnlineStatusMiddleware(BaseHTTPMiddleware):
    OPENAI_STATUS_URL = "https://status.openai.com/api/v2/status.json"

    def __init__(
        self, 
        app: FastAPI, 
        exempt_routes: list[str] = [], 
        *args, 
        **kwargs
    ):
        super().__init__(app, *args, **kwargs)
        self.exempt_routes = exempt_routes
        # 세션을 미들웨어 초기화 시 생성하여 재사용
        self.session = aiohttp.ClientSession()

    async def __call__(
        self, 
        scope: Scope, 
        receive: Receive, 
        send: Send
    ) -> None:
        # HTTP 요청이 아닌 경우 원래 앱 호출
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        # 인증 면제 경로 체크
        if any(request.url.path.endswith(route) for route in self.exempt_routes):
            await self.app(scope, receive, send)
            return

        try:
            async with self.session.get(self.OPENAI_STATUS_URL) as response:
                if response.status == 500:
                    # 경로가 '/gemma'로 끝나지 않을 때만 리다이렉트
                    if not request.url.path.endswith('/gemma'):
                        redirect_url = request.url.path + '/gemma'
                        redirect_response = RedirectResponse(url=redirect_url)
                        await redirect_response(scope, receive, send)
                        return
                    else:
                        # 이미 '/gemma'로 끝나는 경우 원래 요청 처리
                        await self.app(scope, receive, send)
                        return
                elif response.status == 200:
                    status_data = await response.json()
                    description = status_data.get("status", {}).get("description", "")
                    if description.lower() != "all systems operational":
                        raise HTTPException(
                            status_code=503,
                            detail=f"Online Service in Error: {description}",
                        )
                else:
                    raise HTTPException(
                        status_code=503,
                        detail="Service Error...",
                    )
        except aiohttp.ClientError:
            # 상태 페이지 접근 실패 시 원래 요청 처리
            await self.app(scope, receive, send)
            return

        # 정상적인 경우 원래 요청 처리
        await self.app(scope, receive, send)

class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI 미들웨어: 요청과 응답을 로깅하는 미들웨어
    """
    
    def __init__(
        self, 
        app: FastAPI, 
        logger: Optional[logging.Logger] = None
    ):
        self.app = app
        self.logger = logger or get_logger()
    
    async def __call__(
        self, 
        scope: Scope,
        receive: Receive, 
        send: Send
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        request = Request(scope)
        request_id = str(uuid.uuid4())
        
        # 요청 본문 캡처
        request_body = await self._get_request_body(request, receive)
        
        # 요청 로깅
        self.logger.info(f"Request [{request_id}]: {request.method} {request.url.path}")
        self.logger.info(f"Request [{request_id}] Headers: {dict(request.headers)}")
        self.logger.info(f"Request [{request_id}] Body: {request_body}")
        
        # 응답 캡처를 위한 send 래퍼
        response_body = []
        send_wrapper = self._create_send_wrapper(send, response_body, request_id)
        
        # 원래 앱 호출
        await self.app(scope, self._receive_wrapper(receive, request_body), send_wrapper)
    
    async def _get_request_body(self, request: Request, receive: Receive) -> str:
        """요청 본문을 캡처"""
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
        
        try:
            return json.loads(body.decode())
        except (UnicodeDecodeError, json.JSONDecodeError):
            return f"<Binary data: {len(body)} bytes>"
    
    def _create_send_wrapper(self, send: Send, response_body: list, request_id: str) -> Send:
        """응답 본문을 캡처하는 send 래퍼 생성"""
        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                self.logger.info(
                    f"Response [{request_id}]: Status {message.get('status', 'unknown')}"
                )
            
            if message["type"] == "http.response.body":
                body = message.get("body", b"")
                if body:
                    response_body.append(body)
                
                if not message.get("more_body", False):
                    # 응답이 완료되면 전체 본문 로깅
                    full_body = b"".join(response_body)
                    try:
                        decoded_body = json.loads(full_body.decode())
                        self.logger.debug(f"Response [{request_id}] Body: {decoded_body}")
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        self.logger.debug(f"Response [{request_id}] Body: <Binary data: {len(full_body)} bytes>")
            
            await send(message)
        
        return send_wrapper
    
    def _receive_wrapper(self, receive: Receive, request_body: str) -> Receive:
        """원래 요청 본문을 복원하는 receive 래퍼"""
        async def receive_wrapper() -> Message:
            message = await receive()
            if message["type"] == "http.request":
                # 요청 본문 복원
                if isinstance(request_body, dict):
                    body = json.dumps(request_body).encode()
                elif isinstance(request_body, str):
                    body = request_body.encode()
                else:
                    body = b""
                
                message["body"] = body
            
            return message
        
        return receive_wrapper
