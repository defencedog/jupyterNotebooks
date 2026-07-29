"""
N₂ Purge Simulation for Hydrogen Line Maintenance
==================================================
Simulates the inerting of H₂ pipelines with nitrogen before
welding/repair work. Covers dilution modelling, JT cooling
from cylinder expansion, and safety time calculations.

Key safety context:
  - H₂ LEL in air: 4% vol  (but we use N₂, not air)
  - Target for hot work: <1% H₂  (typically 0.5% for welding)
  - N₂ cylinder: ~200 bar
  - JT cooling of N₂ can reach -40°C at high Δp → material concerns
"""

import pyromat as pm
import numpy as np
import matplotlib.pyplot as plt

pm.config['unit_pressure'] = 'bar'
pm.config['unit_temperature'] = 'K'
pm.config['unit_energy'] = 'kJ'

# Substance models
n2 = pm.get('mp.N2')       # real gas — accurate JT, density
h2 = pm.get('ig.H2')       # ideal gas — adequate for conc. calc.

# ------------------------------------------------------------------
# 1.  Scenario Parameters
# ------------------------------------------------------------------
# Hydrogen line
LINE_LENGTH = 50.0          # m
LINE_DIAMETER = 0.15        # m  (6 inch schedule 40)
LINE_VOLUME = np.pi * (LINE_DIAMETER/2)**2 * LINE_LENGTH   # m³
LINE_VOLUME_L = LINE_VOLUME * 1000                          # litres
LINE_PRESSURE = 1.5          # bar(a)  — typical H₂ supply pressure
LINE_TEMP = 303.15           # K  (30 °C)

# Initial H₂ concentration (before purging)
INITIAL_H2_PCT = 100.0       # % vol  (pure H₂ initially)

# Target safe concentration
TARGET_H2_PCT = 0.5          # % vol  (for hot work)
LEL_H2 = 4.0                # % vol  (lower explosive limit in air)
SAFE_MARGIN = 0.125         # 1/8 of LEL — typical safe limit

# Purge gas (N₂) supply
N2_CYLINDER_PRESSURE = 200.0   # bar
N2_REGULATOR_SET = 3.0         # bar  (regulator outlet to line)
N2_TEMPERATURE = 303.15        # K  (ambient before expansion)

# Purge flow parameters
PURGE_FLOW_NM3H = 50.0        # Nm³/h  (normal cubic metres per hour)
# Convert Nm³/h to actual m³/s at line conditions
# Using ideal gas law: V_actual = V_norm * (P_norm/P_actual) * (T_actual/T_norm)
P_NORM = 1.01325               # bar
T_NORM = 273.15                # K
PURGE_FLOW_ACTUAL = (PURGE_FLOW_NM3H / 3600) * (P_NORM / LINE_PRESSURE) * (LINE_TEMP / T_NORM)

# Mixing efficiency (0 = plug flow perfect, 1 = perfectly mixed)
# Real purges are between 0.3–0.7
MIXING_EFFICIENCIES = [0.3, 0.5, 0.7, 1.0]

# ------------------------------------------------------------------
# 2.  Helper Functions
# ------------------------------------------------------------------
def jt_coeff(substance, T, p):
    """Joule-Thomson coefficient via central difference (K/bar)."""
    T = np.asarray(T); p = np.asarray(p)
    scalar = T.ndim == 0
    T = np.atleast_1d(T); p = np.atleast_1d(p)
    EPS = 1e-6
    cp = np.array([float(substance.cp(T=tt, p=pp)) for tt, pp in zip(T.flat, p.flat)])
    dp = EPS * p
    h_p = np.array([float(substance.h(T=tt, p=pp+dp_)) for tt, pp, dp_ in zip(T.flat, p.flat, dp.flat)])
    h_m = np.array([float(substance.h(T=tt, p=pp-dp_)) for tt, pp, dp_ in zip(T.flat, p.flat, dp.flat)])
    dh_dp = (h_p - h_m) / (2.0 * dp)
    mu = -dh_dp / cp
    return float(mu[0]) if scalar else mu

def n2_temperature_after_expansion(T_in, p_in, p_out):
    """Temperature of N₂ after isenthalpic expansion from p_in to p_out."""
    h_in = float(n2.h(T=T_in, p=p_in))
    return float(n2.T(h=h_in, p=p_out))

def h2_concentration_after_purge(N_volumes, efficiency=0.5):
    """H₂ concentration (% vol) after N purge volumes with mixing efficiency η.
    
    C/C₀ = (1 - η)^N
    η = 1 → perfect mixing (exponential decay)
    η → 0 → plug flow (sharp front, no decay until 1 volume)
    """
    return INITIAL_H2_PCT * (1 - efficiency) ** N_volumes

def purge_volumes_to_target(efficiency, target=TARGET_H2_PCT):
    """Number of line volumes required to reach target concentration."""
    if efficiency <= 0:
        return float('inf')
    if efficiency >= 1.0:
        # Perfect mixing: C/C₀ = exp(-N), so N = ln(C₀/C)
        return np.log(INITIAL_H2_PCT / target)
    return np.log(target / INITIAL_H2_PCT) / np.log(1 - efficiency)

# ------------------------------------------------------------------
# 3.  JT Cooling Analysis
# ------------------------------------------------------------------
# Temperature drop across regulator: 200 bar → regulator set pressure
T_after_reg = n2_temperature_after_expansion(N2_TEMPERATURE,
                                              N2_CYLINDER_PRESSURE,
                                              N2_REGULATOR_SET)
JT_drop_reg = N2_TEMPERATURE - T_after_reg

# Temperature drop from regulator to line pressure (final let-down)
T_after_line = n2_temperature_after_expansion(T_after_reg,
                                              N2_REGULATOR_SET,
                                              LINE_PRESSURE)
JT_drop_line = T_after_reg - T_after_line

# Overall temperature drop
T_final_n2 = T_after_line
JT_drop_total = N2_TEMPERATURE - T_final_n2

# JT coefficient at various conditions (for reference)
T_scan = np.linspace(250, 350, 11)
mu_vs_T_200 = np.array([jt_coeff(n2, T, 200.0) for T in T_scan])
mu_vs_T_3   = np.array([jt_coeff(n2, T, N2_REGULATOR_SET) for T in T_scan])
mu_vs_T_1_5 = np.array([jt_coeff(n2, T, LINE_PRESSURE) for T in T_scan])

# ------------------------------------------------------------------
# 4.  Dilution Model
# ------------------------------------------------------------------
N_max = 12
N_volumes = np.arange(0, N_max + 1)

# Concentration decay for each mixing efficiency
decay_curves = {}
for eta in MIXING_EFFICIENCIES:
    decay_curves[eta] = h2_concentration_after_purge(N_volumes, eta)

# Purge volumes needed for each efficiency
purge_vols_needed = {eta: purge_volumes_to_target(eta) for eta in MIXING_EFFICIENCIES}

# ------------------------------------------------------------------
# 5.  Time and Consumption
# ------------------------------------------------------------------
# Time for one line volume exchange at actual flow rate
TIME_PER_VOLUME = LINE_VOLUME / PURGE_FLOW_ACTUAL   # seconds

# N₂ mass per line volume at line conditions
density_n2_line = float(n2.d(T=T_final_n2, p=LINE_PRESSURE))  # kg/m³
mass_n2_per_volume = density_n2_line * LINE_VOLUME   # kg

# Time and N₂ consumption to reach target for each efficiency
purge_data = []
for eta in MIXING_EFFICIENCIES:
    N_req = purge_vols_needed[eta]
    time_req = N_req * TIME_PER_VOLUME / 60.0   # minutes
    mass_req = N_req * mass_n2_per_volume        # kg
    # Nm³ consumed (at normal conditions)
    density_n2_norm = float(n2.d(T=T_NORM, p=P_NORM))
    nm3_req = mass_req / density_n2_norm
    purge_data.append({
        'efficiency': eta,
        'volumes': N_req,
        'time_min': time_req,
        'mass_kg': mass_req,
        'nm3': nm3_req,
    })

# ------------------------------------------------------------------
# 6.  Plots
# ------------------------------------------------------------------
SAVE_DIR = '/home/ukhan/engg/ukhan/proj/pyromat_ukhan/'

# ---- 6.1  JT Cooling Profile ----
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(T_scan - 273.15, mu_vs_T_200, 'o-', color='#1f77b4', linewidth=2,
        label='200 bar (cylinder)')
ax.plot(T_scan - 273.15, mu_vs_T_3, 's-', color='#ff7f0e', linewidth=2,
        label=f'{N2_REGULATOR_SET} bar (regulator out)')
ax.plot(T_scan - 273.15, mu_vs_T_1_5, '^-', color='#2ca02c', linewidth=2,
        label=f'{LINE_PRESSURE} bar (line)')
ax.axhline(0, color='gray', linewidth=0.6, linestyle='--')
ax.set_xlabel('Temperature (°C)', fontsize=12)
ax.set_ylabel('μ_JT  (K / bar)', fontsize=12)
ax.set_title('N₂ Joule-Thomson Coefficient\nat Cylinder, Regulator, and Line Pressures',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(SAVE_DIR + 'n2_purge_jt_coefficient.png', dpi=150)
plt.close()
print("[1/6] JT coefficient → n2_purge_jt_coefficient.png")


# ---- 6.2  Temperature Drop Across Expansion Stages ----
stages = ['Cylinder\n200 bar', 'Regulator\n3 bar', 'Line\n1.5 bar']
temps = [N2_TEMPERATURE - 273.15, T_after_reg - 273.15, T_final_n2 - 273.15]
drops = [0, JT_drop_reg, JT_drop_total]

fig, ax1 = plt.subplots(figsize=(8, 5))
bars = ax1.bar(stages, temps, color=['#1f77b4', '#ff7f0e', '#2ca02c'],
               edgecolor='black', width=0.5, zorder=3)
ax1.set_ylabel('Temperature (°C)', fontsize=12, color='b')
ax1.tick_params(axis='y', labelcolor='b')
for bar, val in zip(bars, temps):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f'{val:.1f}°C', ha='center', fontsize=10, fontweight='bold')

ax2 = ax1.twinx()
ax2.plot(stages, drops, 'ro-', linewidth=2, markersize=8, zorder=4,
         label='Cumulative ΔT')
ax2.set_ylabel('Cumulative ΔT  (°C)', fontsize=12, color='r')
ax2.tick_params(axis='y', labelcolor='r')
for i, d in enumerate(drops):
    if d != 0:
        ax2.annotate(f'-{d:.1f}°C', (stages[i], d),
                     textcoords='offset points', xytext=(10, 10),
                     fontsize=9, color='r', fontweight='bold')

ax1.set_title('N₂ Temperature Through Expansion Stages\n'
              f'Total JT cooling: {JT_drop_total:.1f} °C  |  '
              f'T_final = {T_final_n2 - 273.15:.1f} °C',
              fontsize=13, fontweight='bold')
ax1.grid(True, axis='y', alpha=0.3)
fig.tight_layout()
plt.savefig(SAVE_DIR + 'n2_purge_temperature_drop.png', dpi=150)
plt.close()
print("[2/6] Temperature drop → n2_purge_temperature_drop.png")


# ---- 6.3  H₂ Concentration Decay ----
fig, ax = plt.subplots(figsize=(10, 6))
colors_eta = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
line_styles = ['-', '--', '-.', ':']

for eta, c, ls in zip(MIXING_EFFICIENCIES, colors_eta, line_styles):
    ax.semilogy(N_volumes, decay_curves[eta], color=c, linestyle=ls,
                linewidth=2, marker='o', markersize=4,
                label=f'η = {eta}  ({purge_vols_needed[eta]:.1f} vols)')

ax.axhline(TARGET_H2_PCT, color='gray', linewidth=1.5, linestyle='--',
           label=f'Target: {TARGET_H2_PCT}%')
ax.axhline(LEL_H2, color='r', linewidth=1.5, linestyle=':',
           label=f'LEL: {LEL_H2}%')

ax.set_xlabel('Number of Purge Volumes Exchanged', fontsize=12)
ax.set_ylabel('H₂ Concentration  (% vol)', fontsize=12)
ax.set_title('H₂ Concentration Decay During N₂ Purge\n'
             f'Line: {LINE_LENGTH}m × {LINE_DIAMETER*1000:.0f}mm ID  |  '
             f'Volume: {LINE_VOLUME_L:.0f} L',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=9, title='η (vols to target)')
ax.grid(True, alpha=0.3, which='both')
ax.set_xlim(0, N_max)
ax.set_ylim(0.01, 200)
plt.tight_layout()
plt.savefig(SAVE_DIR + 'n2_purge_concentration_decay.png', dpi=150)
plt.close()
print("[3/6] Concentration decay → n2_purge_concentration_decay.png")


# ---- 6.4  Purge Time & N₂ Consumption ----
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Time to safe concentration
etas_plot = [e for e in MIXING_EFFICIENCIES]
times_plot = [purge_vols_needed[e] * TIME_PER_VOLUME / 60 for e in etas_plot]
nm3_plot = [purge_vols_needed[e] * mass_n2_per_volume /
            float(n2.d(T=T_NORM, p=P_NORM)) for e in etas_plot]

bars1 = ax1.bar([str(e) for e in etas_plot], times_plot,
                color=colors_eta[:len(etas_plot)], edgecolor='black', width=0.5)
ax1.set_xlabel('Mixing Efficiency η', fontsize=12)
ax1.set_ylabel('Time to Safe Concentration  (min)', fontsize=12)
ax1.set_title('Purge Duration', fontsize=13, fontweight='bold')
for bar, val in zip(bars1, times_plot):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
             f'{val:.1f} min', ha='center', fontsize=10, fontweight='bold')
ax1.grid(True, axis='y', alpha=0.3)

bars2 = ax2.bar([str(e) for e in etas_plot], nm3_plot,
                color=colors_eta[:len(etas_plot)], edgecolor='black', width=0.5)
ax2.set_xlabel('Mixing Efficiency η', fontsize=12)
ax2.set_ylabel('N₂ Consumption  (Nm³)', fontsize=12)
ax2.set_title('Nitrogen Consumption', fontsize=13, fontweight='bold')
for bar, val in zip(bars2, nm3_plot):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
             f'{val:.1f} Nm³', ha='center', fontsize=10, fontweight='bold')
ax2.grid(True, axis='y', alpha=0.3)

fig.suptitle(f'Purge Requirements for {LINE_VOLUME_L:.0f} L H₂ Line\n'
             f'Purge flow: {PURGE_FLOW_NM3H} Nm³/h  |  '
             f'Target: ≤{TARGET_H2_PCT}% H₂',
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(SAVE_DIR + 'n2_purge_time_consumption.png', dpi=150)
plt.close()
print("[4/6] Purge time & consumption → n2_purge_time_consumption.png")


# ---- 6.5  Parametric: Volume vs. Efficiency Contour ----
line_volumes = np.logspace(1, 3, 50)  # 10 to 1000 L
efficiencies = np.linspace(0.2, 1.0, 50)
V_grid, E_grid = np.meshgrid(line_volumes, efficiencies)
# Time to target (minutes) for each combination
with np.errstate(divide='ignore'):
    N_req_grid = np.where(E_grid < 1.0,
                          np.log(TARGET_H2_PCT / INITIAL_H2_PCT) / np.log(1 - E_grid),
                          np.log(INITIAL_H2_PCT / TARGET_H2_PCT))
flow_actual_grid = (PURGE_FLOW_NM3H / 3600) * (P_NORM / LINE_PRESSURE) * (LINE_TEMP / T_NORM)
time_grid = N_req_grid * (V_grid / 1000) / flow_actual_grid / 60

fig, ax = plt.subplots(figsize=(9, 6))
contour = ax.contourf(V_grid, E_grid, time_grid, levels=20, cmap='RdYlBu_r')
cbar = plt.colorbar(contour, ax=ax, label='Time to safe conc.  (min)')
ax.contour(V_grid, E_grid, time_grid, levels=[5, 10, 15, 30, 60],
           colors='k', linewidths=0.8)
ax.clabel(ax.contour(V_grid, E_grid, time_grid, levels=[5, 10, 15, 30, 60],
                      colors='k', linewidths=0.8), inline=True, fontsize=9)
ax.axvline(LINE_VOLUME_L, color='g', linewidth=2, linestyle='--',
           label=f'This line: {LINE_VOLUME_L:.0f} L')
ax.set_xlabel('Line Volume  (L)', fontsize=12)
ax.set_ylabel('Mixing Efficiency  η', fontsize=12)
ax.set_title('Purge Time Sensitivity\n'
             f'Flow: {PURGE_FLOW_NM3H} Nm³/h  |  Target: ≤{TARGET_H2_PCT}% H₂',
             fontsize=13, fontweight='bold')
ax.legend()
ax.set_xscale('log')
plt.tight_layout()
plt.savefig(SAVE_DIR + 'n2_purge_sensitivity.png', dpi=150)
plt.close()
print("[5/6] Sensitivity contour → n2_purge_sensitivity.png")


# ---- 6.6  Safety Envelope ----
N_detailed = np.linspace(0, N_max, 200)
fig, ax = plt.subplots(figsize=(10, 6))

# Shaded safety zones
ax.axhspan(0, SAFE_MARGIN * LEL_H2, alpha=0.15, color='green',
           label=f'Safe for hot work  (H₂ < {SAFE_MARGIN*LEL_H2:.2f}%)')
ax.axhspan(SAFE_MARGIN * LEL_H2, LEL_H2, alpha=0.15, color='gold',
           label=f'Marginal  ({SAFE_MARGIN*LEL_H2:.2f}–{LEL_H2}%)')
ax.axhspan(LEL_H2, 100, alpha=0.15, color='red',
           label=f'EXPLOSIVE  (> {LEL_H2}%)')

for eta, c, ls in zip(MIXING_EFFICIENCIES, colors_eta, line_styles):
    conc = h2_concentration_after_purge(N_detailed, eta)
    ax.plot(N_detailed, conc, color=c, linestyle=ls, linewidth=2,
            label=f'η = {eta}')

# Markers for key points
for eta in MIXING_EFFICIENCIES:
    N_safe = purge_volumes_to_target(eta, SAFE_MARGIN * LEL_H2)
    if np.isfinite(N_safe):
        ax.axvline(N_safe, color=colors_eta[MIXING_EFFICIENCIES.index(eta)],
                   linewidth=0.8, linestyle=':', alpha=0.6)
        ax.annotate(f'{N_safe:.1f}', (N_safe, 0.3),
                    fontsize=8, color=colors_eta[MIXING_EFFICIENCIES.index(eta)],
                    rotation=90, va='bottom')

ax.set_xlabel('Number of Purge Volumes', fontsize=12)
ax.set_ylabel('H₂ Concentration  (% vol)', fontsize=12)
ax.set_title('Safety Envelope During N₂ Purge\n'
             f'Line at {LINE_PRESSURE} bar, {LINE_TEMP-273.15:.0f} °C',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=9, loc='upper right')
ax.set_ylim(0, 20)
ax.set_xlim(0, N_max)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(SAVE_DIR + 'n2_purge_safety_envelope.png', dpi=150)
plt.close()
print("[6/6] Safety envelope → n2_purge_safety_envelope.png")

# ------------------------------------------------------------------
# 7.  Summary Printout
# ------------------------------------------------------------------
print(f"""
{'='*65}
  N₂ PURGE SIMULATION — HYDROGEN LINE INERTING
{'='*65}

LINE SPECIFICATIONS
  Length:              {LINE_LENGTH:.0f} m
  Diameter:            {LINE_DIAMETER*1000:.0f} mm  ({LINE_DIAMETER*39.37:.1f} in)
  Volume:              {LINE_VOLUME_L:.0f} L  ({LINE_VOLUME:.3f} m³)
  Operating pressure:  {LINE_PRESSURE:.1f} bar(a)
  Temperature:         {LINE_TEMP-273.15:.0f} °C

JT COOLING (N₂ expansion 200 → 1.5 bar)
  After regulator:     {T_after_reg-273.15:.1f} °C  (ΔT = {JT_drop_reg:.1f} °C)
  In line:             {T_final_n2-273.15:.1f} °C  (ΔT = {JT_drop_total:.1f} °C)
  μ_JT at 30°C:        {jt_coeff(n2, 303.15, 200.0):.3f} K/bar  (200 bar)
                       {jt_coeff(n2, 303.15, 1.5):.3f} K/bar  (1.5 bar)

PURGE FLOW
  Normal flow rate:    {PURGE_FLOW_NM3H} Nm³/h
  Actual flow rate:    {PURGE_FLOW_ACTUAL:.4f} m³/s  ({PURGE_FLOW_ACTUAL*1000:.1f} L/s)
  Time per volume:     {TIME_PER_VOLUME:.1f} s
  N₂ density in line:  {density_n2_line:.3f} kg/m³
  N₂ per volume:       {mass_n2_per_volume:.3f} kg

DILUTION TO ≤{TARGET_H2_PCT}% H₂
  η     Volumes   Time(min)   N₂(kg)   N₂(Nm³)  Feasible?
  {'-'*55}
""")
for d in purge_data:
    feasible = '✓' if d['volumes'] < 30 else '✗ (too many)'
    print(f"  {d['efficiency']:<5.1f}  {d['volumes']:<9.1f} {d['time_min']:<10.1f} "
          f"{d['mass_kg']:<8.2f} {d['nm3']:<9.1f} {feasible}")

feasible_data = [p for p in purge_data if p['volumes'] < 30]
best_purge = min(feasible_data, key=lambda p: p['volumes']) if feasible_data else purge_data[0]
print(f"""
RECOMMENDATIONS
  • Minimum purge:     {best_purge['volumes']:.1f} volumes (η = {best_purge['efficiency']})
  • Expected time:     {best_purge['time_min']:.1f} min
  • N₂ consumption:    {best_purge['nm3']:.1f} Nm³
  • Verify with:       Portable H₂ detector at vent
  • Material caution:  N₂ at {T_final_n2-273.15:.0f}°C may approach MDMT
                       of carbon steel piping (typically -29°C)
""")

print("All plots saved to pyromat_ukhan/")