## 核心原则

1. **使用sqlmodel实现**：使用sqlmodel库来构建数据库模型。
2. **使用有意义的命名**：选择描述性强的变量、函数和类名。
3. **遵循 PEP 8 规范**：遵守 Python 增强提案 8 的代码格式指南。
4. **编写文档字符串**：使用文档字符串说明函数和类的用途。
5. **保持简洁性**：编写简单清晰的代码，避免不必要的复杂性。


## 示例

```python
class PromptCreate(SQLModel):
    name: str
    label: list[str]
    prompt: str


class PromptBase(SQLModel):
    fid: uuid.UUID = Field(default_factory=uuid.uuid4, index=True)
    name: str = Field(max_length=128)
    have_keys: bool = False
    # 返回给前端时，处理成list
    label: list[str] = []
    keys: list[str] = []
    counter: int = 0
    prompt: str = Field(max_length=1024 * 10)


class Prompt(PromptBase, table=True):
    __tablename__ = "prompts"

    id: int | None = Field(primary_key=True, index=True, default=None)
    is_delete: bool = Field(
        default=False,
        sa_column=Column(Integer, default=0, comment="是否共享，0表示否，1表示是"),
    )
    label: str = Field(max_length=128)
    keys: str = Field(max_length=512)
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now)
```