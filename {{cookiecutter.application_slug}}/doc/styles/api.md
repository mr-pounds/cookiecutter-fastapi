## 核心原则

1. **使用有意义的命名**：选择描述性强的变量、函数和类名。
2. **遵循 PEP 8 规范**：遵守 Python 增强提案 8 的代码格式指南。
3. **编写文档字符串**：使用文档字符串说明函数和类的用途。
4. **保持简洁性**：编写简单清晰的代码，避免不必要的复杂性。
5. **优先使用列表推导式**：在适当场景下，优先使用列表推导式而非传统循环创建列表。
6. **异常处理**：使用 try-except 块优雅地处理异常。
7. **类型注解**：使用类型提示增强代码可读性和类型检查，编写类型注解代码需遵守@ai_models 规范。

## 示例

```python
from fastapi import APIRouter, Query
from sqlmodel import select

from app.api.deps import SessionDep
from app.exception import DataDoesNotExist
from app.response import ListResponseModel
from app.models.agent import Prompt, PromptBase

router = APIRouter()

@router.get("/prompt", response_model=ListResponseModel[PromptBase])
def get_prompt(
    *, session: SessionDep, label: str = Query(None), content: str = Query(None)
):
    statement = select(Prompt).where(Prompt.is_delete == 0)
    if label:
        statement = statement.where(Prompt.label.like(f"%{label}%"))
        label_statement = select(PromptLabel).where(PromptLabel.label == label)
        label_obj = session.exec(label_statement).first()
        if label_obj:
            # 给label的计数器+1
            label_obj.counter += 1
            session.add(label_obj)
            session.commit()

    if content:
        statement = statement.where(Prompt.prompt.like(f"%{content}%"))

    prompts = session.exec(statement).all()
    return ListResponseModel(
        data={
            "list": [
                PromptBase.model_validate(
                    obj,
                    update={
                        "label": ast.literal_eval(obj.label),
                        "keys": ast.literal_eval(obj.keys),
                    },
                )
                for obj in prompts
            ],
            "total": len(prompts),
        }
    )
```