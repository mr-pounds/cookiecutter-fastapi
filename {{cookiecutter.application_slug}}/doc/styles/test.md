## 核心原则

1. **使用 pytest 实现**：使用 pytest 库来进行单元测试。
2. 独立性：测试之间不相互依赖，使用mock隔离外部依赖。
3. 可重复性：测试结果一致，不依赖外部状态。
4. 全面性：覆盖所有逻辑分支，包括异常。
5. 明确断言：验证预期结果，确保测试有效性。
6. 高覆盖率：尽可能覆盖代码，但不过度追求。

## 示例

```python
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.config import settings
from app.models.agent import Prompt

def test_create_and_update_prompt(client: TestClient, db: Session) -> None:
    # 创建一个 Prompt 实例数据
    r = client.post(
        f"{settings.API_V1_STR}/agents/create_prompt",
        json={
            "name": PROMPT_NAME,
            "label": ["test_label"],
            "prompt": "test_prompt",
        },
    )

    # 验证返回状态码
    assert r.status_code == 200

    # 验证数据库中是否存在该 Prompt 实例
    statement = select(Prompt).where(Prompt.name == PROMPT_NAME)
    db_prompt = db.exec(statement).first()
    assert db_prompt
    assert db_prompt.counter == 0

    # 测试更新 Prompt 实例
    r = client.put(
        f"{settings.API_V1_STR}/agents/update_prompt/{db_prompt.fid}",
        json={
            "name": PROMPT_NAME,
            "label": ["update_label"],
            "prompt": "updated_prompt",
        },
    )

    # 验证返回状态码
    assert r.status_code == 200

    # 验证数据库中 Prompt 实例是否更新成功
    db.refresh(db_prompt)
    assert db_prompt.prompt == "updated_prompt"
    assert db_prompt.label == str(["update_label"])

    # 测试更新 counter 字段
    r = client.get(f"{settings.API_V1_STR}/agents/add_counter/{db_prompt.fid}")
    assert r.status_code == 200
    # 验证数据库中 Prompt 实例的 counter 字段是否更新成功
    db.refresh(db_prompt)
    assert db_prompt.counter == 1
```