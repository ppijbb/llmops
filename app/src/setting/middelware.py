from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Scope, Receive, Send
import aiohttp
from starlette.responses import RedirectResponse

class OnlineStatusMiddleware(BaseHTTPMiddleware):
    OPENAI_STATUS_URL = "https://status.openai.com/api/v2/status.json"

    def __init__(self, app: FastAPI, exempt_routes: list[str] = [], *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.exempt_routes = exempt_routes
        # 세션을 미들웨어 초기화 시 생성하여 재사용
        self.session = aiohttp.ClientSession()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
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
                    print("API Status Check Successed")
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
