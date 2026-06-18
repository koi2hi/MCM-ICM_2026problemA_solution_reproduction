import numpy as np
import matplotlib.pyplot as plt

# 1. 物理参数设置 (与前面一致，使用修正后的参数)
Q_n = 3.3 * 3600  
V_cutoff = 3.0    
eta = 0.95        
R_0 = 0.12        
R_1 = 0.03        
C_1 = 1000        
R_tot = R_0 + R_1 

def get_ocv(soc):
    """非线性开路电压公式"""
    return 3.3 + 0.9 * soc - 0.2 * np.exp(-30 * soc)

# 2. 模拟函数 (针对 Figure 6，我们只需要跑单个场景)
def simulate_brownout(P_load, initial_soc):
    soc = initial_soc
    V_1 = 0.0     
    time = 0.0    
    
    history_time = []
    history_soc = []
    history_voltage = []
    
    while soc > 0:
        ocv = get_ocv(soc)
        discriminant = (ocv - V_1)**2 - 4 * R_tot * (P_load / eta)
        
        if discriminant < 0:
            break
            
        I = ((ocv - V_1) - np.sqrt(discriminant)) / (2 * R_tot)
        V_term = ocv - I * R_0 - V_1
        
        history_time.append(time / 3600)
        history_soc.append(soc * 100)
        history_voltage.append(V_term)
        
        if V_term <= V_cutoff:
            break
            
        dV1_dt = (I / C_1) - (V_1 / (R_1 * C_1))
        V_1 += dV1_dt * 2.0  # dt = 2.0s
        soc -= (I * 2.0) / Q_n
        time += 2.0
        
    return history_time, history_soc, history_voltage

# 我们设定和 Figure 6 一模一样的条件：Gaming 场景，初始电量 20% (0.2)
t, s, v = simulate_brownout(P_load=3.67, initial_soc=0.20)

# ==========================================
# 3. 画图：完美复现 Figure 6 的双 Y 轴格式
# ==========================================
fig, ax1 = plt.subplots(figsize=(10, 6))

# 设置左边 Y 轴 (画电压)
color_v = 'tab:blue'
ax1.set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Terminal Voltage (V)', color=color_v, fontsize=12, fontweight='bold')
line1 = ax1.plot(t, v, color=color_v, linewidth=2.5, label='Terminal Voltage')
ax1.tick_params(axis='y', labelcolor=color_v)
# 画出红色的关机线
line2 = ax1.axhline(y=V_cutoff, color='tab:red', linestyle='--', linewidth=2, label='Cutoff Voltage (3.0V)')
# 锁定电压 Y 轴的范围，和原图一致
ax1.set_ylim(2.8, 4.0) 

# 创建共享 X 轴的第二个 Y 轴 (画电量)
ax2 = ax1.twinx()  
color_s = 'tab:green'
ax2.set_ylabel('State of Charge (%)', color=color_s, fontsize=12, fontweight='bold')  
line3 = ax2.plot(t, s, color=color_s, linewidth=2.5, linestyle='-.', label='SOC')
ax2.tick_params(axis='y', labelcolor=color_s)
# 锁定电量 Y 轴的范围
ax2.set_ylim(0, 25)

# 合并图例
lines = line1 + [line2] + line3
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper right', shadow=True)

# 添加标注框说明 Brownout 机制
ax1.annotate('Voltage drops faster than SOC\ndue to high current draw', 
             xy=(t[-1], v[-1]), 
             xytext=(t[-1]-0.2, v[-1]+0.3),
             arrowprops=dict(facecolor='black', arrowstyle='->', lw=2),
             bbox=dict(boxstyle="round,pad=0.4", fc="wheat", alpha=0.8),
             fontsize=11)

plt.title('Brownout Mechanism: Voltage Sag Under High Load\n(Gaming scenario, 20% initial SOC)', fontweight='bold')
ax1.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.show()