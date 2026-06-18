import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 准备数据 (提取自原论文 Figure 13 与 Table 4)
# ==========================================
# 以每天典型轻中度使用 8 小时 (480分钟) 为基准线

# 建议名称 (按优化效果从弱到强排序)
recommendations = [
    "Close Background Apps",                 # 关闭后台应用
    "Enable Dark Mode (Indoor)",             # 室内开启深色模式
    "Batch Network Sync",                    # 集中处理网络同步
    "Prefer Wi-Fi over Cellular",            # 优先使用 WiFi
    "Reduce CPU/GPU Load (Gaming)",          # 降低游戏画质/帧率
    "Lower Screen Brightness (100%->50%)",   # 降低屏幕亮度
    "Enable Dark Mode (Outdoor)"             # 户外高亮度下开启深色模式
]

# 向右的收益数据：延长的时间 (分钟) 与 对应的百分比
gain_mins = [24, 48, 48, 72, 120, 168, 192]
gain_pcts = [5, 10, 10, 15, 25, 35, 40]

# 向左的代价数据：如果不这么做，损失的时间 (分钟) 与 百分比
loss_mins = [-12, -14, -24, -38, -72, -96, -120]
loss_pcts = [-2, -3, -5, -8, -15, -20, -25]

# 根据收益百分比划分颜色等级 (完美还原论文配色)
# High (>20%): 深蓝色 | Medium (10-20%): 浅蓝色 | Low (<10%): 浅绿色
colors = []
for pct in gain_pcts:
    if pct > 20:
        colors.append('#4A6EA9') # 深蓝 (High)
    elif pct >= 10:
        colors.append('#8EBAE5') # 浅蓝 (Medium)
    else:
        colors.append('#A5E075') # 浅绿 (Low)

# ==========================================
# 2. 绘制图表主体：双向条形图
# ==========================================
fig, ax = plt.subplots(figsize=(12, 8))
y_pos = np.arange(len(recommendations))
bar_height = 0.65

# 画向右的收益柱 (彩色)
rects_gain = ax.barh(y_pos, gain_mins, height=bar_height, color=colors, edgecolor='gray', alpha=0.9)

# 画向左的损失柱 (统一用浅灰色)
rects_loss = ax.barh(y_pos, loss_mins, height=bar_height, color='#B0B8C1', edgecolor='gray', alpha=0.6)

# 画中间的 0 分钟基准黑线
ax.axvline(0, color='black', linewidth=1.5)

# ==========================================
# 3. 添加文字标注
# ==========================================
# 3.1 为右侧柱子添加收益文字 (+分钟, +%)
for i, rect in enumerate(rects_gain):
    ax.text(rect.get_width() + 5, rect.get_y() + rect.get_height()/2, 
            f'+{gain_mins[i]} min\n(+{gain_pcts[i]}%)', 
            va='center', ha='left', fontsize=9, fontweight='bold', color='black')

# 3.2 为左侧柱子添加代价文字 (-分钟, -%)
for i, rect in enumerate(rects_loss):
    ax.text(rect.get_width() - 5, rect.get_y() + rect.get_height()/2, 
            f'{loss_mins[i]} min\n({loss_pcts[i]}%)', 
            va='center', ha='right', fontsize=9, color='gray')

# ==========================================
# 4. 图表美化与细节还原
# ==========================================
# 设置 Y 轴标签
ax.set_yticks(y_pos)
ax.set_yticklabels(recommendations, fontsize=10)
# 让 Y 轴的名字靠着中间这根线远一点，避免重叠
ax.tick_params(axis='y', pad=10)

# 设置 X 轴
ax.set_xlim(-200, 230)
ax.set_xlabel('Change in Time-to-Empty (minutes)', fontsize=12, fontweight='bold')
ax.set_title('Tornado Chart: Prioritized User Recommendations for Battery Life Extension\nBaseline Scenario: 8 hours (480 min) under typical usage', 
             fontsize=13, fontweight='bold', pad=20)

# 添加背景网格虚线
ax.grid(axis='x', linestyle='--', alpha=0.5)
# 隐藏上、右、左侧的图表边框线
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

# ==========================================
# 5. 添加论文原图的说明框 (Model Insight & 图例)
# ==========================================
# 添加“模型洞察”文本框 (左上角)
insight_text = ("Model Insight:\n"
                "Screen brightness management yields\n"
                "the highest cost-benefit ratio,\n"
                "while closing background apps\n"
                "provides marginal gains.")
ax.text(-190, 6, insight_text, fontsize=10, fontweight='bold',
        bbox=dict(boxstyle="round,pad=0.5", facecolor='#FFF8DC', edgecolor='gray', alpha=0.8))

# 添加自定义的颜色分类图例框 (右上角)
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#4A6EA9', edgecolor='gray', label='High Impact (>20% improvement)'),
    Patch(facecolor='#8EBAE5', edgecolor='gray', label='Medium Impact (10-20% improvement)'),
    Patch(facecolor='#A5E075', edgecolor='gray', label='Low Impact (<10% improvement)')
]
ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.0, 1.05),
          frameon=True, shadow=True, facecolor='white', edgecolor='black', fontsize=9)

# 调整布局以适应长标签
plt.tight_layout()

# 反转 Y 轴，让影响最大的排在最下面 (符合原论文排版)
ax.invert_yaxis()

# 显示图像
plt.show()