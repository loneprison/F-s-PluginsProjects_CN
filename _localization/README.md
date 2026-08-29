# 本地化文本目录

人工维护内容包括插件源码中的 Original 文本及其对应的 JSON catalog。Original 使用完整的 `L10N_*` 宏名，JSON 中不重复保存 Original。

## JSON

每个效果只有一个同名 JSON。已迁移目录册的 `translations` 先按语言、再按源码扫描得到的 `Param`、`Label`、`Popup`、`Topic`、`About` 和 `Error` 分区；最终格式不保存 `bindings` 或 Original。

- 每个需要翻译的 ID 都填写非空字符串、精确 `{"useSource": true}` 或由显式同步命令生成的 `null`。
- `{"useSource": true}` 固定写成单行；其余结构使用两空格缩进。
- 缺失或 `null` 表示尚未完成，不等同于使用原文，出版校验会拒绝。

```json
{
  "schemaVersion": 1,
  "translations": {
    "en": {
      "Param": {
        "L10N_PARAM_REVERSE": {"useSource": true}
      },
      "Popup": {
        "L10N_PARAM_ITEMS": {"useSource": true}
      }
    },
    "zh": {
      "Param": {
        "L10N_PARAM_REVERSE": "反转"
      },
      "Popup": {
        "L10N_PARAM_ITEMS": "甲|乙|丙"
      }
    }
  }
}
```

编辑规则：

- ID 必须与源码中实际存在的 `L10N_*` 字符串宏完全一致。
- 不要填写空翻译。
- Popup 翻译的 `|` 分段数量、空项和精确分隔项 `(-` 的位置必须与 Original 一致。

Language Settings 使用单独的 `catalog/_Support/Settings.json`，其 `entries` 项直接包含 `id`、`token`、`zh`、`en`、`ja`。
