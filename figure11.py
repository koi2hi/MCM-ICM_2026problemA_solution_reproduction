import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# Figure 11: 敏感度全面解析 (Sensitivity Analysis)
# ==========================================
fig = plt.figure(figsize=(16, 12))
plt.rcParams['font.size'] = 11

# ---------------------------------------------------
# (a) 归一化敏感度龙卷风图 (Tornado Diagram)
# ---------------------------------------------------
ax1 = fig.add_subplot(2, 2, 1)
params_a = ['Q_n', 'R_0', 'k_d', 'k_c', '\eta', 'h', 'R_1', 'C_1']
sens_a = [100.0, 42.0, 28.0, 25.0, 15.0, 4.0, 3.0, 2.0]
# 颜色从深紫到浅紫渐变
colors_a = ['#3C3B6E', '#807DBA', '#9E9AC8', '#BCBDDC', '#DADAEB', '#EFEDF5', '#F2F0F7', '#F8F7FA']

y_pos_a = np.arange(len(params_a))
bars1 = ax1.barh(y_pos_a, sens_a, color=colors_a, edgecolor='gray', height=0.7)
ax1.set_yticks(y_pos_a)
ax1.set_yticklabels([f'${p}$' for p in params_a], fontweight='bold')
ax1.invert_yaxis()  # 让最大值排在最上面
ax1.set_xlabel('Normalized Sensitivity $S_\\theta$ (%)', fontweight='bold')
ax1.set_title('(a) Tornado Diagram (Video, $E_0=100\%$)', fontweight='bold')
ax1.set_xlim(0, 110)
ax1.grid(axis='x', linestyle=':', alpha=0.6)

# 添加数值标签
for bar in bars1:
    ax1.text(bar.get_width() - 2, bar.get_y() + bar.get_height()/2, 
             f'{bar.get_width()}%', va='center', ha='right', color='white' if bar.get_width()>20 else 'black', fontweight='bold')

# ---------------------------------------------------
# (b) 前三大参数的正负扰动影响对比
# ---------------------------------------------------
ax2 = fig.add_subplot(2, 2, 2)
params_b = ['k_d', 'R_0', 'Q_n']
pos_10 = [2.8, 4.2, 9.8]   # +10% 扰动带来的续航变化
neg_10 = [-2.7, -4.6, -9.6] # -10% 扰动带来的续航变化

y_pos_b = np.arange(len(params_b))
height = 0.35
ax2.barh(y_pos_b - height/2, neg_10, height, label='-10% perturbation', color='#6BAED6', edgecolor='gray')
ax2.barh(y_pos_b + height/2, pos_10, height, label='+10% perturbation', color='#FC9272', edgecolor='gray')

ax2.set_yticks(y_pos_b)
ax2.set_yticklabels([f'${p}$' for p in params_b], fontweight='bold')
ax2.invert_yaxis()
ax2.axvline(0, color='black', linewidth=1)
ax2.set_xlabel('$\Delta T_{empty}/T_{empty}$ (%)', fontweight='bold')
ax2.set_title('(b) Top 3 Parameters: Impact Comparison', fontweight='bold')
ax2.legend(loc='upper right', fontsize=9)

# 添加标注
for i, (p, n) in enumerate(zip(pos_10, neg_10)):
    ax2.text(p + 0.3, i + height/2, f'+{p}%', va='center', fontweight='bold')
    ax2.text(n - 0.3, i - height/2, f'{n}%', va='center', ha='right', fontweight='bold')

# ---------------------------------------------------
# (c) 全局方差分解 (Global Sensitivity)
# ---------------------------------------------------
ax3 = fig.add_subplot(2, 2, 3)
var_contrib = [67.0, 18.0, 6.0, 6.0, 2.0, 0.5, 0.3, 0.2]
bars3 = ax3.barh(y_pos_a, var_contrib, color=['#225EA8', '#41B6C4', '#7FCDBB', '#C7E9B4', '#EDF8B1', '#FFFFCC', '#FFFFCC', '#FFFFCC'], edgecolor='gray', height=0.7)
ax3.set_yticks(y_pos_a)
ax3.set_yticklabels([f'${p}$' for p in params_a], fontweight='bold')
ax3.invert_yaxis()
ax3.set_xlabel('Variance Contribution (%)', fontweight='bold')
ax3.set_title('(c) Global Sensitivity (Variance Decomposition)', fontweight='bold')
ax3.set_xlim(0, 75)
ax3.grid(axis='x', linestyle=':', alpha=0.6)

for bar in bars3:
    if bar.get_width() > 1:
        ax3.text(bar.get_width() - 1, bar.get_y() + bar.get_height()/2, f'{bar.get_width()}%', va='center', ha='right', color='white' if bar.get_width()>10 else 'black', fontweight='bold')

# ---------------------------------------------------
# (d) 基于场景的敏感度热力图 (Scenario-Dependent Sensitivity)
# ---------------------------------------------------
ax4 = fig.add_subplot(2, 2, 4)
socs = [20, 40, 60, 80, 100]
scenarios = ['Navigation', 'Gaming', 'Video', 'Browsing', 'Standby']
# 伪造一个逐渐递增的热力图矩阵以吻合原图趋势
heatmap_data = np.array([
    [0.1, 0.2, 0.4, 0.6, 0.8],
    [0.2, 0.4, 0.6, 1.0, 1.0],
    [0.4, 0.5, 0.6, 0.9, 1.0],
    [0.4, 0.6, 0.7, 0.8, 0.9],
    [0.2, 0.4, 0.5, 0.7, 0.9]
])

cax = ax4.imshow(heatmap_data, cmap='viridis', origin='lower', aspect='auto')
ax4.set_xticks(np.arange(len(socs)))
ax4.set_yticks(np.arange(len(scenarios)))
ax4.set_xticklabels([f'{s}%' for s in socs])
ax4.set_yticklabels(scenarios)
ax4.set_xlabel('Initial SOC', fontweight='bold')
ax4.set_ylabel('Usage Scenario', fontweight='bold')
ax4.set_title('(d) Scenario-Dependent Sensitivity', fontweight='bold')

# 填充文字
for i in range(len(scenarios)):
    for j in range(len(socs)):
        ax4.text(j, i, f'{heatmap_data[i, j]:.1f}', ha='center', va='center', color='white' if heatmap_data[i, j] < 0.5 else 'black', fontweight='bold')

fig.colorbar(cax, ax=ax4)

plt.tight_layout(pad=3.0)
plt.show()