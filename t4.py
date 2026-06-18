import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# Figure 12: 电池耗尽的核心驱动因素 (Key Drivers)
# ==========================================
fig = plt.figure(figsize=(16, 12))
plt.rcParams['font.size'] = 11

# ---------------------------------------------------
# (a) 场景硬件功耗拆解 (Power Breakdown by Component)
# ---------------------------------------------------
ax1 = fig.add_subplot(2, 2, 1)
scenarios_a = ['Standby', 'Browsing', 'Video', 'Gaming', 'Navigation']
# 各模块的功耗数据 (W)
bg_power = np.array([0.05, 0.1, 0.1, 0.3, 0.1])
net_power = np.array([0.1, 0.25, 0.25, 0.35, 0.2])
gps_power = np.array([0.0, 0.0, 0.0, 0.0, 0.4])
cpu_power = np.array([0.05, 0.4, 0.8, 1.2, 0.5])
disp_power = np.array([0.05, 0.8, 1.2, 1.5, 1.2])

x_pos = np.arange(len(scenarios_a))
width = 0.5

# 堆叠柱状图
p1 = ax1.bar(x_pos, disp_power, width, label='Display', color='#DDEBF7', edgecolor='gray')
p2 = ax1.bar(x_pos, cpu_power, width, bottom=disp_power, label='CPU', color='#BDD7EE', edgecolor='gray')
p3 = ax1.bar(x_pos, gps_power, width, bottom=disp_power+cpu_power, label='GPS', color='#E2EFDA', edgecolor='gray')
p4 = ax1.bar(x_pos, net_power, width, bottom=disp_power+cpu_power+gps_power, label='Network', color='#C6E0B4', edgecolor='gray')
p5 = ax1.bar(x_pos, bg_power, width, bottom=disp_power+cpu_power+gps_power+net_power, label='Background', color='#A9D08E', edgecolor='gray')

total_power = disp_power + cpu_power + gps_power + net_power + bg_power
for i, total in enumerate(total_power):
    ax1.text(i, total + 0.1, f'{total:.2f}W', ha='center', fontweight='bold')

ax1.set_xticks(x_pos)
ax1.set_xticklabels(scenarios_a)
ax1.set_ylabel('Power Consumption (W)', fontweight='bold')
ax1.set_xlabel('Usage Scenario', fontweight='bold')
ax1.set_title('(a) Power Breakdown by Component', fontweight='bold')
ax1.legend(loc='upper left', fontsize=9)
ax1.set_ylim(0, 4.5)

# ---------------------------------------------------
# (b) 非线性电压与电流关系 (Voltage-Current Nonlinearity)
# ---------------------------------------------------
ax2 = fig.add_subplot(2, 2, 2)
currents = np.linspace(0, 3.5, 100)
R_internal = 0.12 # 设定内阻
soc_levels_b = [1.0, 0.8, 0.6, 0.4, 0.2]
colors_b = ['#1B9E77', '#7570B3', '#666666', '#D95F02', '#A6761D']

for soc, col in zip(soc_levels_b, colors_b):
    # OCV 简化公式
    ocv = 3.3 + 0.9 * soc - 0.2 * np.exp(-30 * soc)
    v_term = ocv - currents * R_internal
    ax2.plot(currents, v_term, color=col, lw=2.5, label=f'SOC={int(soc*100)}%')

# 标注 Brownout Risk (电压骤降风险区)
ax2.scatter(2.5, 3.05, s=150, facecolors='none', edgecolors='teal', linewidths=3)
ax2.text(2.5, 2.95, 'Brownout\nRisk', color='teal', ha='center', va='top', fontweight='bold')

ax2.set_xlabel('Discharge Current (A)', fontweight='bold')
ax2.set_ylabel('Terminal Voltage (V)', fontweight='bold')
ax2.set_title('(b) Voltage-Current Nonlinearity', fontweight='bold')
ax2.legend(loc='upper right')
ax2.set_xlim(0, 3.5)
ax2.set_ylim(2.7, 4.3)
ax2.grid(True, linestyle=':', alpha=0.6)

# ---------------------------------------------------
# (c) 热效应曲线 (Modest Thermal Effects)
# ---------------------------------------------------
ax3 = fig.add_subplot(2, 2, 3)
time_h = np.linspace(0, 3, 100)
# 使用牛顿冷却定律模拟发热平衡： T(t) = T_env + delta_T * (1 - e^(-t/tau))
T_env = 25.0
ax3.plot(time_h, T_env + 0.5 * (1 - np.exp(-time_h/0.5)), label='Standby', color='#DDEBF7', lw=2)
ax3.plot(time_h, T_env + 1.8 * (1 - np.exp(-time_h/0.5)), label='Browsing', color='#BDD7EE', lw=2)
ax3.plot(time_h, T_env + 3.5 * (1 - np.exp(-time_h/0.8)), label='Video', color='#C6E0B4', lw=2)
ax3.plot(time_h, T_env + 7.8 * (1 - np.exp(-time_h/1.0)), label='Gaming', color='#85C1E9', lw=2)
ax3.axhline(T_env, color='gray', linestyle='-.', alpha=0.5, label='Ambient (25°C)')

ax3.scatter(3.0, 32.8, s=100, color='#1B9E77')
ax3.text(2.9, 33.2, '32.8°C', ha='right', fontweight='bold')

ax3.set_xlabel('Time (hours)', fontweight='bold')
ax3.set_ylabel('Battery Temperature (°C)', fontweight='bold')
ax3.set_title('(c) Modest Thermal Effects', fontweight='bold')
ax3.legend(loc='lower right')
ax3.set_xlim(0, 3.0)
ax3.set_ylim(24, 35)
ax3.grid(True, linestyle=':', alpha=0.6)

# ---------------------------------------------------
# (d) 影响因素重要性综合排名 (Driver Importance Ranking)
# ---------------------------------------------------
ax4 = fig.add_subplot(2, 2, 4)
drivers = ['Polarization\nC1', 'Thermal\nh', 'Efficiency\n$\eta$', 'Resistance\n$R_0$', 'Capacity\n$Q_n$', 'Power\nConsumption']
importance = [2, 4, 28, 42, 81, 88]
y_pos_d = np.arange(len(drivers))

# 区分主导因素(Dominant)和次要因素(Negligible)
colors_d = ['#CDE6D3', '#CDE6D3', '#A1D9CE', '#85C1E9', '#85C1E9', '#85C1E9']

bars4 = ax4.barh(y_pos_d, importance, color=colors_d, edgecolor='gray', height=0.6)
ax4.set_yticks(y_pos_d)
ax4.set_yticklabels(drivers)
ax4.set_xlabel('Impact Magnitude (normalized)', fontweight='bold')
ax4.set_title('(d) Driver Importance Ranking', fontweight='bold')
ax4.set_xlim(0, 100)
ax4.grid(axis='x', linestyle=':', alpha=0.6)

# 自定义图例
from matplotlib.patches import Patch
legend_elements_d = [Patch(facecolor='#85C1E9', edgecolor='gray', label='Dominant'),
                     Patch(facecolor='#CDE6D3', edgecolor='gray', label='Negligible')]
ax4.legend(handles=legend_elements_d, loc='lower right')

for bar in bars4:
    ax4.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, 
             f'{bar.get_width()}', va='center', fontweight='bold')

plt.tight_layout(pad=3.0)
plt.show()