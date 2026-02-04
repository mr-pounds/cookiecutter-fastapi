"""
API集成测试
测试所有API端点的功能，包括认证、会话管理等
"""

from fastapi.testclient import TestClient

from app.schema.auth import SendVerificationCodeHandlerBody
from app.schema.session import CreateSessionBody


class TestAPI:
    """API集成测试类"""

    def test_send_verification_code_success(self, client: TestClient):
        """测试发送验证码成功"""
        body = SendVerificationCodeHandlerBody(phone="13800138000")
        response = client.post("/api/send_verification_code", json=body.model_dump())
        # 验证接口可以正常调用，可能返回200成功、403或429发送频繁
        assert response.status_code in [200, 403, 429]
        data = response.json()
        assert "success" in data
        assert "msg" in data

    def test_send_verification_code_invalid_phone(self, client: TestClient):
        """测试发送验证码失败 - 无效手机号"""
        body = SendVerificationCodeHandlerBody(
            phone="12345678901"
        )  # 11位但格式不正确的手机号
        response = client.post("/api/send_verification_code", json=body.model_dump())
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_send_verification_code_short_phone(self, client: TestClient):
        """测试发送验证码失败 - 手机号长度不足"""
        body = SendVerificationCodeHandlerBody(phone="138001")
        response = client.post("/api/send_verification_code", json=body.model_dump())
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_send_verification_code_long_phone(self, client: TestClient):
        """测试发送验证码失败 - 手机号长度过长"""
        body = SendVerificationCodeHandlerBody(phone="138001380000")
        response = client.post("/api/send_verification_code", json=body.model_dump())
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_get_phone_unauthorized(self, client: TestClient):
        """测试获取手机号失败 - 未授权"""
        response = client.get("/api/get_phone")
        assert response.status_code in [401, 403]

    def test_create_session_unauthorized(self, client: TestClient):
        """测试创建会话失败 - 未授权"""
        body = CreateSessionBody(
            material_url="test_material_url",
            # paper_url="test_paper_url",
            integrate_gear=1,
        )
        response = client.post("/api/create_session", json=body.model_dump())
        assert response.status_code in [401, 403]

    def test_get_left_session_quota_unauthorized(self, client: TestClient):
        """测试获取剩余会话配额失败 - 未授权"""
        response = client.get("/api/get_left_session_quota")
        assert response.status_code in [401, 403]

    def test_get_history_sessions_unauthorized(self, client: TestClient):
        """测试获取历史会话失败 - 未授权"""
        response = client.get("/api/get_history_sessions")
        assert response.status_code in [401, 403]

    def test_get_left_chat_quota_unauthorized(self, client: TestClient):
        """测试获取剩余聊天配额失败 - 未授权"""
        response = client.get("/api/get_left_chat_quota?session_id=test_session")
        assert response.status_code in [401, 403, 400]
