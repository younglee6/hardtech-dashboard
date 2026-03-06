# 牛市顶部监测看板（实时版）设计规格

## 1. 目标
- 每天 1 分钟判断市场阶段：正常 / 中后期 / 高风险 / 顶部。
- 实时拉取核心数据，自动评分、自动预警、自动给出动作建议。

## 2. 看板结构（单页）
- 模块A：总评分卡（今日分数 + 阶段 + 建议动作）
- 模块B：五大指标评分（情绪/估值/流动性/结构/技术）
- 模块C：风险信号灯（任一触发即红色）
- 模块D：7日趋势（总分与各指标变化）

## 3. 数据模型（建议一张宽表 + 一张行情表）

### 表1：`daily_top_signals`
- `date`（date）
- `fear_greed_value`（number）
- `sp500_pe`（number）
- `us10y_yield`（number）
- `us10y_ma5`（number）
- `market_divergence_flag`（boolean，指数涨但个股跌=1）
- `sp500_rsi14`（number）
- `one_day_spx_return`（number）
- `hot_sector_surge_flag`（boolean）
- `retail_fomo_news_flag`（boolean）
- `ipo_crypto_boom_flag`（boolean）

### 表2：`market_breadth_intraday`（可选）
- `timestamp`（datetime）
- `spx_return_intraday`（number）
- `advancers_decliners_ratio`（number）
- `new_high_count`（number）

## 4. 评分规则（Tableau 计算字段）

### 4.1 五大分项
- `score_sentiment`
  - `IF [fear_greed_value] > 80 THEN 1 ELSE 0 END`
- `score_valuation`
  - `IF [sp500_pe] > 25 THEN 1 ELSE 0 END`
- `score_liquidity`
  - `IF [us10y_yield] > [us10y_ma5] THEN 1 ELSE 0 END`
- `score_structure`
  - `IF [market_divergence_flag] = TRUE THEN 1 ELSE 0 END`
- `score_technical`
  - `IF [sp500_rsi14] > 70 THEN 1 ELSE 0 END`

### 4.2 总分与阶段
- `total_score`
  - `[score_sentiment] + [score_valuation] + [score_liquidity] + [score_structure] + [score_technical]`
- `market_phase`
  - `IF [total_score] <= 2 THEN "正常"`
  - `ELSEIF [total_score] = 3 THEN "中后期"`
  - `ELSEIF [total_score] = 4 THEN "高风险"`
  - `ELSE "顶部" END`

### 4.3 操作建议
- `action_suggestion`
  - `IF [total_score] <= 2 THEN "持有"`
  - `ELSEIF [total_score] = 3 THEN "观察"`
  - `ELSEIF [total_score] = 4 THEN "减仓30%"`
  - `ELSE "减仓50%" END`

### 4.4 风险信号灯
- `risk_signal_on`
  - `IF [one_day_spx_return] > 0.02`
  - `OR [hot_sector_surge_flag] = TRUE`
  - `OR [retail_fomo_news_flag] = TRUE`
  - `OR [ipo_crypto_boom_flag] = TRUE`
  - `THEN 1 ELSE 0 END`

## 5. 可视化布局（Tableau 单页 Dashboard）
- 顶部横条（KPI）：
  - 今日日期
  - 总分（大号数字）
  - 阶段（颜色编码：绿/黄/橙/红）
  - 操作建议（标签）
- 中部左侧（五大指标）：
  - 五个圆点或条形，每项 0/1
  - 鼠标悬浮显示阈值与原始值
- 中部右侧（风险灯）：
  - 红/灰状态灯
  - 下方列出触发项明细
- 底部（趋势）：
  - 最近 7/30 天 `total_score` 折线
  - 次轴叠加 `fear_greed_value` 和 `sp500_rsi14`

## 6. 刷新频率与实时性
- 高频（每15分钟）：`us10y_yield`、指数涨跌、结构信号
- 日频（每日收盘后）：`sp500_pe`、RSI、恐慌贪婪
- Tableau 刷新建议：
  - 工作时段：15分钟
  - 非工作时段：60分钟

## 7. 数据源建议（按可实现优先级）
- FRED：10Y 国债收益率（稳定，API 友好）
- Yahoo Finance：SPX 行情、技术指标计算原料
- 手工/半自动输入：恐慌贪婪指数（如暂无法直接 API）
- 自定义脚本生成 `market_divergence_flag`（指数与广度背离）

## 8. 最小可用版本（MVP）
- 只接 6 个字段：`date/fear_greed_value/sp500_pe/us10y_yield/market_divergence_flag/sp500_rsi14`
- 自动生成：五大分项 + 总分 + 阶段 + 建议
- 一页看板 + 一个风险灯

## 9. 质量控制
- 每日开盘前检查昨日数据是否落库
- 对空值做保护：空值默认0分并标注“数据缺失”
- 分数计算写入单元测试（脚本层）防止阈值被误改

## 10. 你今天就能用的版本
- 第一步：先在 Tableau 用 CSV 建 `daily_top_signals`
- 第二步：按第4节添加计算字段
- 第三步：按第5节拖拽出一页 Dashboard
- 第四步：把数据源替换为 API 同步后的表，开启定时刷新
