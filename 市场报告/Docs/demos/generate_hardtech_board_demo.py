import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig = plt.figure(figsize=(9, 16), facecolor='#0B1220')

# Title area
ax_title = fig.add_axes([0.06, 0.88, 0.88, 0.1])
ax_title.axis('off')
ax_title.text(0.0, 0.78, 'HARD TECH DAILY BOARD', fontsize=24, color='#7DD3FC', fontweight='bold')
ax_title.text(0.0, 0.48, '2026-03-04 · 小红书看板 Demo', fontsize=14, color='#C7D2FE')
ax_title.text(0.0, 0.12, 'AI / Chip / Robotics / EV', fontsize=12, color='#93C5FD')

# Breakthrough cards
ax_cards = fig.add_axes([0.06, 0.66, 0.88, 0.2])
ax_cards.set_facecolor('#101A2E')
ax_cards.set_xticks([])
ax_cards.set_yticks([])
for spine in ax_cards.spines.values():
    spine.set_visible(False)

cards = [
    ('交互突破', 'Claude Code 语音化\nAI 编程进入口述时代'),
    ('基建突破', 'AI-Native 6G 路线推进\n通信网络变成算力底座'),
    ('车端突破', 'VLA 智驾迭代 + 超快充预期\nEV 从卖车转向卖系统能力')
]

x_positions = [0.03, 0.35, 0.67]
for i, (title, text) in enumerate(cards):
    x = x_positions[i]
    rect = plt.Rectangle((x, 0.12), 0.28, 0.76, color='#16233F', ec='#334155', lw=1.2)
    ax_cards.add_patch(rect)
    ax_cards.text(x + 0.02, 0.72, title, fontsize=12, color='#FDE68A', fontweight='bold')
    ax_cards.text(x + 0.02, 0.36, text, fontsize=10.5, color='#E2E8F0', linespacing=1.4)

ax_cards.text(0.02, 0.95, '今日 3 大技术突破点', fontsize=13, color='#A5B4FC', fontweight='bold')

# Pie chart
ax_pie = fig.add_axes([0.06, 0.39, 0.42, 0.22], facecolor='#101A2E')
labels = ['AI', 'Chip', 'Robotics', 'EV']
sizes = [40, 25, 18, 17]
colors = ['#38BDF8', '#818CF8', '#34D399', '#F59E0B']
wedges, texts, autotexts = ax_pie.pie(
    sizes,
    labels=labels,
    colors=colors,
    autopct='%1.0f%%',
    startangle=120,
    textprops={'color': '#E5E7EB', 'fontsize': 10}
)
for at in autotexts:
    at.set_color('#0F172A')
    at.set_fontweight('bold')
ax_pie.set_title('赛道热度占比（Demo）', color='#C7D2FE', fontsize=12, pad=10)

# Heatmap
ax_heat = fig.add_axes([0.54, 0.39, 0.40, 0.22], facecolor='#101A2E')
matrix = np.array([
    [9, 8, 7],   # AI
    [8, 8, 9],   # Chip infra
    [7, 8, 8],   # Robotics
    [8, 9, 8],   # EV tech
])
im = ax_heat.imshow(matrix, cmap='YlGnBu', vmin=0, vmax=10)
ax_heat.set_xticks([0, 1, 2])
ax_heat.set_xticklabels(['近 1 季度', '中期 1 年', '长期 3 年'], color='#E5E7EB', fontsize=9)
ax_heat.set_yticks([0, 1, 2, 3])
ax_heat.set_yticklabels(['AI', 'Chip', 'Robotics', 'EV'], color='#E5E7EB', fontsize=9)
ax_heat.set_title('趋势热力分布（0-10）', color='#C7D2FE', fontsize=12, pad=10)

for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
        ax_heat.text(j, i, str(matrix[i, j]), ha='center', va='center', color='#0F172A', fontsize=10, fontweight='bold')

cbar = fig.colorbar(im, ax=ax_heat, fraction=0.046, pad=0.04)
cbar.ax.yaxis.set_tick_params(color='#CBD5E1')
plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#CBD5E1', fontsize=8)

# Footer
ax_footer = fig.add_axes([0.06, 0.08, 0.88, 0.24])
ax_footer.set_facecolor('#101A2E')
ax_footer.set_xticks([])
ax_footer.set_yticks([])
for spine in ax_footer.spines.values():
    spine.set_visible(False)

footer_lines = [
    '结论 1：AI 竞争从模型参数，转向交互形态 + 组织稳定性 + 合规治理。',
    '结论 2：芯片与网络正在一体化演进，端侧算力与通信底座同步升级。',
    '结论 3：机器人和 EV 都在比“系统工程能力”，不是单点参数。',
    '发布建议：标题用情绪词 + 首图信息长图 + 评论区置顶来源链接。',
    '#AI #芯片 #硬科技 #机器人 #新能源车 #科技早报'
]

ax_footer.text(0.02, 0.88, '今日洞察速记', color='#A5B4FC', fontsize=13, fontweight='bold')
for idx, line in enumerate(footer_lines):
    ax_footer.text(0.02, 0.72 - idx * 0.14, line, color='#E2E8F0', fontsize=11)

out = '/Users/ios15/Documents/New project/市场报告/Docs/demos/hardtech-xhs-infoboard-demo-2026-03-04.png'
fig.savefig(out, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
print(out)
