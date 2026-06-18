import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 构建高级电池物理模型 (引入温度变量)
# ==========================================
class AdvancedBatteryModel:
    def __init__(self):
        self.Q_ref = 3.3 * 3600  # 基准容量 (As)
        self.R0_ref = 0.12       # 25°C 基准内阻
        self.R1 = 0.03           # 极化内阻
        self.C1 = 1000           # 极化电容
        self.V_cutoff = 3.0      # 关机电压
        self.eta = 0.95          # 转换效率
        self.T_ref = 298.15      # 基准温度 (25°C = 298.15K)

    def get_ocv(self, soc):
        """非线性 OCV 函数，保留低电量断崖下跌特性"""
        return 3.3 + 0.9 * soc - 0.2 * np.exp(-30 * soc)

    def get_R0(self, T_celsius):
        """阿伦尼乌斯方程：计算不同温度下的内阻"""
        T_kelvin = T_celsius + 273.15
        # 活化能常数假设为 3000，低温下内阻会显著升高
        return self.R0_ref * np.exp(3000 * (1/T_kelvin - 1/self.T_ref))

    def get_Q_avail(self, T_celsius):
        """低温容量锁定机制：温度越低，可放出的真实电量越少"""
        if T_celsius < 25:
            return self.Q_ref * (1 - 0.006 * (25 - T_celsius))
        return self.Q_ref

    def simulate_tte(self, P_load, initial_soc=1.0, T_celsius=25.0, Q_noise=1.0, R_noise=1.0):
        """
        全量程时间步进求解器，支持注入噪声进行蒙特卡洛模拟
        """
        soc = initial_soc
        V_1 = 0.0
        time = 0.0
        
        # 应用温度和噪声影响
        Q_actual = self.get_Q_avail(T_celsius) * Q_noise
        R0_actual = self.get_R0(T_celsius) * R_noise
        R_tot = R0_actual + self.R1
        
        hist_time, hist_soc = [], []
        
        while soc > 0 and time < 100 * 3600:
            ocv = self.get_ocv(soc)
            discriminant = (ocv - V_1)**2 - 4 * R_tot * (P_load / self.eta)
            
            if discriminant < 0: break # 功率过载物理极限
            
            I = ((ocv - V_1) - np.sqrt(discriminant)) / (2 * R_tot)
            V_term = ocv - I * R0_actual - V_1
            
            if V_term <= self.V_cutoff: break # 低压关机 (Brownout)
                
            hist_time.append(time / 3600)
            hist_soc.append(soc * 100)
            
            # 状态更新
            dV1_dt = (I / self.C1) - (V_1 / (self.R1 * self.C1))
            V_1 += dV1_dt * 5.0  # dt = 5s 加快计算
            soc -= (I * 5.0) / Q_actual
            time += 5.0
            
        return np.array(hist_time), np.array(hist_soc), time / 3600

# 初始化全局模型
model = AdvancedBatteryModel()

# ==========================================
# 2. 复现 Figure 9: 不确定性传播 (Monte Carlo)
# ==========================================
print("正在执行 50 次蒙特卡洛模拟，生成 95% 置信区间 (Figure 9)...")
n_iter = 50
common_time = np.linspace(0, 4, 200) # 统一的时间轴用于插值
soc_matrix = np.zeros((n_iter, 200))

for i in range(n_iter):
    # 为电池容量和内阻加入随机制造误差 (标准差 3%)
    q_noise = np.random.normal(1.0, 0.03)
    r_noise = np.random.normal(1.0, 0.03)
    
    t_hist, s_hist, _ = model.simulate_tte(P_load=3.67, Q_noise=q_noise, R_noise=r_noise)
    
    # 因为每次模拟结束时间不同，需要将其插值到公共时间轴上
    # 如果时间超出了电池耗尽的时间，SOC 记为 NaN
    soc_interp = np.interp(common_time, t_hist, s_hist, right=np.nan)
    soc_matrix[i, :] = soc_interp

# 计算均值和标准差 (忽略 NaN)
mean_soc = np.nanmean(soc_matrix, axis=0)
std_soc = np.nanstd(soc_matrix, axis=0)

fig9, ax9 = plt.subplots(figsize=(8, 5))
ax9.fill_between(common_time, mean_soc - 1.96*std_soc, mean_soc + 1.96*std_soc, 
                 color='blue', alpha=0.3, label='95% Confidence Interval')
ax9.plot(common_time, mean_soc, color='red', lw=2, label='Mean SOC')
ax9.set_xlim(0, 3.5)
ax9.set_ylim(0, 100)
ax9.set_xlabel('Time (hours)', fontweight='bold')
ax9.set_ylabel('State of Charge (%)', fontweight='bold')
ax9.set_title('SOC Decay with Uncertainty Propagation\nGaming Scenario (50 Monte Carlo Iterations)', fontweight='bold')
ax9.legend()
ax9.grid(True, linestyle=':', alpha=0.7)
plt.show()

# ==========================================
# 3. 复现 Figure 10: 鲁棒性分析六宫格
# ==========================================
print("正在生成六宫格鲁棒性分析面板 (Figure 10)...")
fig10 = plt.figure(figsize=(15, 10))

# --- (a) 容量与电阻的独立影响 (双X轴) ---
ax_a1 = fig10.add_subplot(2, 3, 1)
cap_range = np.linspace(0.8, 1.2, 10)  # 相对容量变化 80%~120%
tte_cap = [model.simulate_tte(P_load=2.55, Q_noise=q)[2] for q in cap_range]
ax_a1.plot(cap_range * 3300, tte_cap, 'b-o', label='Battery Capacity')
ax_a1.set_xlabel('Battery Capacity (mAh)', color='blue')
ax_a1.set_ylabel('Time-to-Empty (hours)')
ax_a1.tick_params(axis='x', labelcolor='blue')

ax_a2 = ax_a1.twiny() # 创建顶部X轴
res_range = np.linspace(0.5, 1.5, 10) # 相对内阻变化 50%~150%
tte_res = [model.simulate_tte(P_load=2.55, R_noise=r)[2] for r in res_range]
ax_a2.plot(res_range * 120, tte_res, 'g-o', label='Internal Resistance')
ax_a2.set_xlabel('Internal Resistance R0 (mΩ)', color='green')
ax_a2.tick_params(axis='x', labelcolor='green')
plt.title('(a) Capacity & Resistance Effects', y=1.15, fontweight='bold')

# --- (b) 温度鲁棒性 ---
ax_b = fig10.add_subplot(2, 3, 2)
temps = np.linspace(-20, 45, 15)
tte_temp = [model.simulate_tte(P_load=2.55, T_celsius=t)[2] for t in temps]
ax_b.plot(temps, tte_temp, 'purple', marker='D', lw=2)
ax_b.axvspan(-20, 0, color='blue', alpha=0.1, label='Cold Zone')
ax_b.axvspan(35, 45, color='red', alpha=0.1, label='Hot Zone')
ax_b.axvline(25, color='black', linestyle='--', alpha=0.5, label='Reference 25°C')
ax_b.set_xlabel('Ambient Temperature (°C)')
ax_b.set_ylabel('Time-to-Empty (hours)')
ax_b.set_title('(b) Temperature Robustness', fontweight='bold')
ax_b.legend(loc='lower right')

# --- (c) 负载功率鲁棒性 ---
ax_c = fig10.add_subplot(2, 3, 3)
powers = np.linspace(0.5, 6.0, 20)
tte_power = [model.simulate_tte(P_load=p)[2] for p in powers]
ax_c.plot(powers, tte_power, color='lightseagreen', lw=2, marker='.')
ax_c.axvline(2.55, color='darkred', linestyle='--', label='Nominal 2.5W')
ax_c.axvspan(4.0, 6.0, color='red', alpha=0.1, label='Extreme Load')
ax_c.set_xlabel('Load Power $P_{load}$ (W)')
ax_c.set_ylabel('Time-to-Empty (hours)')
ax_c.set_title('(c) Load Power Robustness', fontweight='bold')
ax_c.legend()

# --- (d) 低电量下的电压骤降 (V-I 特性) ---
ax_d = fig10.add_subplot(2, 3, 4)
soc_vals = np.linspace(0, 1, 100)
ocv_vals = model.get_ocv(soc_vals)
ax_d.plot(soc_vals*100, ocv_vals - 1.0 * model.R0_ref, label='Light (1A)', color='green')
ax_d.plot(soc_vals*100, ocv_vals - 2.0 * model.R0_ref, label='Medium (2A)', color='blue')
ax_d.plot(soc_vals*100, ocv_vals - 3.5 * model.R0_ref, label='Heavy (3.5A)', color='red')
ax_d.axhline(3.0, color='black', linestyle='--', label='$V_{cutoff}$')
ax_d.fill_between(soc_vals*100, 2.6, 3.0, color='red', alpha=0.1)
ax_d.set_ylim(2.6, 4.2)
ax_d.set_xlabel('State of Charge (%)')
ax_d.set_ylabel('Terminal Voltage (V)')
ax_d.set_title('(d) Voltage Sag at Low SOC', fontweight='bold')
ax_d.legend()

# --- (e) 复合压力条件柱状图 ---
ax_e = fig10.add_subplot(2, 3, 5)
conditions = ['Normal\n25°C, 50%', 'Cold\n-10°C, 50%', 'Low SOC\n25°C, 15%', 'Combined\n-10°C, 15%']
tte_e = [
    model.simulate_tte(P_load=3.67, initial_soc=0.5, T_celsius=25)[2],
    model.simulate_tte(P_load=3.67, initial_soc=0.5, T_celsius=-10)[2],
    model.simulate_tte(P_load=3.67, initial_soc=0.15, T_celsius=25)[2],
    model.simulate_tte(P_load=3.67, initial_soc=0.15, T_celsius=-10)[2],
]
colors = ['green', 'blue', 'orange', 'red']
bars = ax_e.bar(conditions, tte_e, color=colors, edgecolor='black')
for bar in bars:
    ax_e.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.05, 
              f'{bar.get_height():.2f}h', ha='center', fontweight='bold')
ax_e.set_ylabel('Time-to-Empty (hours)')
ax_e.set_title('(e) Combined Stress Conditions', fontweight='bold')

# --- (f) 各场景预测稳定性 (CV变异系数) ---
ax_f = fig10.add_subplot(2, 3, 6)
scenarios = {"Standby": 0.139, "Browsing": 0.845, "Video": 1.78, "Navigation": 1.415, "Gaming": 3.67}
cv_results = []
for p in scenarios.values():
    # 对每种场景施加 10% 随机噪声测试其 CV
    tte_samples = [model.simulate_tte(P_load=p, Q_noise=np.random.normal(1.0, 0.1))[2] for _ in range(30)]
    cv = (np.std(tte_samples) / np.mean(tte_samples)) * 100
    cv_results.append(cv)

x_pos = np.arange(len(scenarios))
bars_f = ax_f.bar(x_pos, cv_results, color='#FAD7A1', edgecolor='black')
for bar in bars_f:
    ax_f.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.2, 
              f'{bar.get_height():.1f}%', ha='center')
ax_f.axhline(6.0, color='red', linestyle='--', alpha=0.5, label='High Variability')
ax_f.set_xticks(x_pos)
ax_f.set_xticklabels(scenarios.keys())
ax_f.set_ylabel('Coefficient of Variation (%)')
ax_f.set_title('(f) Prediction Stability', fontweight='bold')
ax_f.legend()

plt.tight_layout()
plt.show()