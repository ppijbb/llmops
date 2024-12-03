import os

import logging
from typing import Any, List, Dict
import time
import traceback
import requests
import httpx
import websockets
import asyncio

from fastapi import FastAPI, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, Response
from ray import serve
from ray.serve.handle import DeploymentHandle

from app.src.engine import OpenAIService, get_gpt_service
from app.dto import SummaryRequest, SummaryResponse
from app.utils.text_process import text_preprocess, text_postprocess
from app.logger import get_logger


router = APIRouter()

# @serve.deployment
# @serve.ingress(app=router)
class DemoRouterIngress:
    def __init__(
        self, 
        llm_handle: DeploymentHandle = None
        ) -> None:
        if llm_handle is not None:
            self.service = llm_handle
        self.demo_address = "192.168.1.55:8504"
        self.server_logger = get_logger()
    
    @router.get("/health")
    async def healthcheck(
        self,
    ):
        try:
            return {"message": "ok"}
        except Exception as e:
            self.server_logger.error("error" + e)
            return Response(
                    content=f"Summary Service Can not Reply",
                    status_code=500
                )
    
    @router.api_route(
        "/{path:path}", 
        response_class=Response, 
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        include_in_schema=False)
    async def serve_streamlit(self,path: str, request: Request):
        """
        FastAPI에서 들어온 요청을 Streamlit 서버로 전달하고 응답을 반환합니다.
        """
        async with httpx.AsyncClient() as client:
            # 요청 메타데이터 추출
            url = f"http://{self.demo_address}/{path}"  # 요청 경로 재구성
            # 요청을 Streamlit 서버로 전달
            try:
                streamlit_response = await client.request(
                    method=request.method,
                    url=url,
                    headers=request.headers,
                    content=await request.body(),
                    # cookies=request.cookies,
                    timeout=3.0
                )
            except httpx.RequestError as e:
                return Response(
                    content=f"Error connecting to Streamlit server: {e}",
                    status_code=502
                )

            # 응답 변환 후 반환 (비-스트리밍 방식)
            return Response(
                content=streamlit_response.content,
                status_code=streamlit_response.status_code,
                headers={key: value for key, value in streamlit_response.headers.items() if key.lower() != "content-encoding"}
            )

    @router.api_route(
        "/static/{path:path}", 
        response_class=Response, 
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        include_in_schema=False)
    async def serve_streamlit(self,path: str, request: Request):
        """
        FastAPI에서 들어온 요청을 Streamlit 서버로 전달하고 응답을 반환합니다.
        """
        async with httpx.AsyncClient() as client:
            # 요청 메타데이터 추출
            method = request.method
            url = f"http://{self.demo_address}/static/{path}"  # 요청 경로 재구성
            headers = dict(request.headers)
            body = await request.body()
            cookies = request.cookies


            # 요청을 Streamlit 서버로 전달
            try:
                streamlit_response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    content=body,
                    cookies=cookies,
                    timeout=3.0
                )
            except httpx.RequestError as e:
                return Response(
                    content=f"Error connecting to Streamlit server: {e}",
                    status_code=502
                )

            # 응답 변환 후 반환 (비-스트리밍 방식)
            return Response(
                content=streamlit_response.content,
                status_code=streamlit_response.status_code,
                headers={key: value for key, value in streamlit_response.headers.items() if key.lower() != "content-encoding"}
            )
            
    @router.api_route(
        "/_stcore/{path:path}", 
        response_class=Response, 
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        include_in_schema=False)
    async def serve_streamlit(self, path: str, request: Request):
        """
        FastAPI에서 들어온 요청을 Streamlit 서버로 전달하고 응답을 반환합니다.
        """
        async with httpx.AsyncClient() as client:
            # 요청 메타데이터 추출
            method = request.method
            url = f"http://{self.demo_address}/_stcore/{path}"  # 요청 경로 재구성
            headers = dict(request.headers)
            body = await request.body()
            cookies = request.cookies

            # 요청을 Streamlit 서버로 전달
            try:
                streamlit_response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    content=body,
                    cookies=cookies,
                    timeout=3.0
                )
            except httpx.RequestError as e:
                return Response(
                    content=f"Error connecting to Streamlit server: {e}",
                    status_code=502
                )

            # 응답 변환 후 반환 (비-스트리밍 방식)
            return Response(
                content=streamlit_response.content,
                status_code=streamlit_response.status_code,
                headers={key: value for key, value in streamlit_response.headers.items() if key.lower() != "content-encoding"}
            )
            
    @router.websocket(
        "/{path:path}")
    async def proxy_websocket(self, path: str, websocket: WebSocket):
        """
        FastAPI에서 WebSocket 요청을 Streamlit 서버로 중계하며, 쿠키를 전달하고,
        WebSocket 연결을 적절히 업그레이드합니다.
        """
        await websocket.accept()  # 클라이언트 WebSocket 연결 수락

        # 클라이언트의 요청 헤더에서 쿠키 추출
        cookies = websocket.headers.get('cookie', '')  # 클라이언트에서 받은 쿠키를 추출

        # WebSocket 연결에 사용할 HTTP 헤더 (쿠키 및 Upgrade 헤더 포함)
        headers = {
            "X-Forwarded-For": websocket.client.host,
            "X-Real-IP": websocket.client.host,
            "Origin": websocket.headers.get("Origin", ""),
            "Upgrade": "websocket",
            "Connection": "Upgrade",
            "Host": websocket.headers.get("Host", ""),
        }
        # Streamlit WebSocket 서버 연결 (쿠키 및 Upgrade 헤더 포함)
        try:
            async with websockets.connect(f"ws://{self.demo_address}/{path}", extra_headers=headers) as streamlit_ws:
                # 클라이언트와 Streamlit 간 메시지 중계
                async def to_streamlit():
                    async for message in websocket.iter_text():
                        await streamlit_ws.send(message)

                async def to_client():
                    async for message in streamlit_ws:
                        await websocket.send_text(message)

                # 양방향 데이터 전송 처리
                await asyncio.gather(to_streamlit(), to_client())
        except Exception as e:
            self.server_logger.error(f"Error while proxying websocket[demo]: {e}")
            await websocket.close()
    
    # @app.websocket(
    #     "/_stcore/{path:path}")
    # async def proxy_websocket(self, path: str, websocket: WebSocket):
    #     """
    #     FastAPI에서 WebSocket 요청을 Streamlit 서버로 중계하며, 쿠키를 전달하고,
    #     WebSocket 연결을 적절히 업그레이드합니다.
    #     """
    #     await websocket.accept()  # 클라이언트 WebSocket 연결 수락

    #     # 클라이언트의 요청 헤더에서 쿠키 추출
    #     cookies = websocket.headers.get('cookie', '')  # 클라이언트에서 받은 쿠키를 추출

    #     # WebSocket 연결에 사용할 HTTP 헤더 (쿠키 및 Upgrade 헤더 포함)
    #     headers = {
    #         "X-Forwarded-For": websocket.client.host,
    #         "X-Real-IP": websocket.client.host,
    #         "Origin": websocket.headers.get("Origin", ""),
    #         "Upgrade": "websocket",
    #         "Connection": "Upgrade",
    #         "Host": websocket.headers.get("Host", ""),
    #     }

    #     # Streamlit WebSocket 서버 연결 (쿠키 및 Upgrade 헤더 포함)
    #     try:
    #         async with websockets.connect(f"ws://{self.demo_address}/_stcore/{path}", extra_headers=headers) as streamlit_ws:
    #             # 클라이언트와 Streamlit 간 메시지 중계
    #             async def to_streamlit():
    #                 async for message in websocket.iter_text():
    #                     await streamlit_ws.send(message)

    #             async def to_client():
    #                 async for message in streamlit_ws:
    #                     await websocket.send_text(message)

    #             # 양방향 데이터 전송 처리
    #             await asyncio.gather(to_streamlit(), to_client())
    #     except Exception as e:
    #         logger.error(f"Error while proxying websocket: {e}")
    #         await websocket.close()
