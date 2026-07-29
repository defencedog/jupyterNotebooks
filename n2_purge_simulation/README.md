# N₂ Purge Simulation for Hydrogen Line Maintenance

---

## 1. Safety Context

Before welding or hot work on a hydrogen pipeline, the line must be **inerted** — all combustible H₂ gas displaced by an inert gas (typically N₂) until the concentration is well below the Lower Explosive Limit (LEL).

| Safety threshold | H₂ concentration | Meaning |
|-----------------|-----------------|---------|
| LEL in air | 4.0 % vol | Minimum for explosion |
| Safe for hot work | ≤ 0.5 % vol | 1/8 of LEL (industry standard) |
| Initial condition | 100 % vol | Pure H₂ before purge |

### Why N₂?

N₂ is the preferred purge gas in chlor-alkali plants because:
- Chemically inert — no reaction with H₂ or pipe materials
- Readily available from on-site N₂ generation or cylinders
- Relatively low cost
- **BUT**: N₂ expansion produces significant JT cooling (see §3)

---

## 2. Dilution Model

### 2.1 Governing Equation

The H₂ concentration after $N$ purge volumes with mixing efficiency $\eta$ follows:

$$
\frac{C}{C_0} = (1 - \eta)^N
$$

| $\eta$ | Physical meaning |
|--------|-----------------|
| $\eta = 0$ | Plug flow — sharp front, no dilution until 1 full volume |
| $\eta = 0.5$ | Moderate mixing — typical for real purge operations |
| $\eta = 0.7$ | Good mixing — well-designed purge with baffles/distributors |
| $\eta = 1.0$ | Perfect mixing — exponential decay $C/C_0 = e^{-N}$ |

### 2.2 Purge Volumes Required

| Efficiency $\eta$ | Volumes to 0.5% | Time (min) | N₂ consumed |
|:-----------------:|:---------------:|:----------:|:-----------:|
| 0.3 | 14.9 | 21.0 | 19.4 Nm³ |
| 0.5 | 7.6 | 10.8 | 10.0 Nm³ |
| **0.7** | **4.4** | **6.2** | **5.8 Nm³** |
| 1.0 (perfect) | 5.3 | 7.5 | 6.9 Nm³ |

The **recommended operating point** is $\eta = 0.7$ achieved through:
- Proper purge gas distributor at the injection point
- Adequate flow velocity ($> 5$ m/s) for turbulent mixing
- Monitoring at a vent point as far from the injection as possible

---

## 3. Joule-Thomson Cooling

### 3.1 The Risk

N₂ from a 200 bar cylinder expanded to 1.5 bar line pressure undergoes **~30 °C of JT cooling**. The gas entering the line is at **~0 °C** — potentially approaching the Minimum Design Metal Temperature (MDMT) of carbon steel piping.

### 3.2 Temperature Profile

| Stage | Pressure | Temperature | ΔT (cumulative) |
|-------|----------|-------------|:---------------:|
| Cylinder | 200 bar | 30 °C | — |
| After regulator | 3 bar | **0.5 °C** | −29.5 °C |
| In pipeline | 1.5 bar | **0.1 °C** | −29.9 °C |

### 3.3 JT Coefficient vs Conditions

| Pressure | $\mu_{JT}$ at 30 °C | Meaning |
|:--------:|:-------------------:|---------|
| 200 bar | 0.070 K/bar | Smaller effect at high P (dense gas, less ideal) |
| 3 bar | 0.201 K/bar | Larger effect near ambient |
| 1.5 bar | 0.207 K/bar | Approaching ideal-gas limit |

### 3.4 Mitigation

If the pipeline MDMT is above 0 °C:
- Use a **pre-heater** before the regulator (electric heat trace or steam)
- Reduce the pressure drop per stage (two-stage let-down)
- Use a different purge gas (e.g., heated N₂ from a vaporiser)
- Limit the purge flow rate to allow heat gain from pipe walls

---

## 4. Results

### 4.1 Concentration Decay (Plot 3)

The semi-log plot of $C_{H2}$ vs purge volumes shows:
- Exponential decay for all mixing efficiencies
- Target concentration (0.5%) reached between 4.4 and 14.9 volumes depending on $\eta$
- The LEL (4%) is crossed within 1–3 volumes for all practical efficiencies

### 4.2 JT Coefficient (Plot 1)

$\mu_{JT}$ of N₂ varies significantly with pressure:
- **High pressure** (200 bar): $\mu_{JT} \approx 0.07$ K/bar — dense gas effects reduce the JT coefficient
- **Low pressure** (1.5 bar): $\mu_{JT} \approx 0.21$ K/bar — approaching the ideal-gas limit
- $\mu_{JT}$ decreases with temperature at all pressures

### 4.3 Temperature Drop (Plot 2)

Two-stage expansion shows:
- **Regulator stage** (200 → 3 bar): −29.5 °C — dominates the total cooling
- **Line let-down** (3 → 1.5 bar): −0.4 °C — minor additional cooling
- **Final temperature**: ~0.1 °C — potentially problematic for carbon steel

### 4.4 Purge Time & Consumption (Plot 4)

For a 50 m × 150 mm ID line (884 L):
- At 50 Nm³/h, each volume exchange takes ~85 seconds
- Total purge time: 6–21 minutes depending on efficiency
- N₂ consumption: 5.8–19.4 Nm³

### 4.5 Sensitivity Contour (Plot 5)

The contour plot shows purge time as a function of line volume and mixing efficiency:
- **Small lines** (< 100 L): purge completes in < 5 minutes
- **Large lines** (> 500 L): purge time becomes sensitive to efficiency
- Green dashed line marks this line (884 L)

### 4.6 Safety Envelope (Plot 6)

Three safety zones:
- **Green** ($H_2 < 0.5\%$): Safe for hot work
- **Yellow** ($0.5\% < H_2 < 4.0\%$): Marginal — monitoring required
- **Red** ($H_2 > 4.0\%$): Explosive — do NOT proceed

---

## 5. Engineering Recommendations

### 5.1 Purge Procedure

| Step | Action | Detail |
|------|--------|--------|
| 1 | Isolate | Close block valves at both ends of the section |
| 2 | Vent | Depressurise to atmospheric via vent stack |
| 3 | Inject N₂ | Connect at one end, vent at the other |
| 4 | Purge | 4.5 line volumes at > 5 m/s flow velocity |
| 5 | Verify | Measure H₂ at the vent point with calibrated detector |
| 6 | Maintain | Slight positive N₂ pressure during repair to prevent backflow |

### 5.2 Material Caution

N₂ at ~0 °C entering carbon steel piping:
- **CS pipe MDMT**: typically −29 °C (for impact-tested material) or warmer
- **Risk**: Below MDMT, the material may be brittle
- **Check**: Verify the pipe specification against the actual temperature
- **Mitigation**: Heat trace or vaporiser if MDMT is borderline

### 5.3 N₂ Consumption

From 200 bar cylinders (standard 50 L cylinder ≈ 10 Nm³):

| Cylinders required | For this purge |
|:------------------:|:--------------:|
| 1 | Small line, good efficiency |
| 2 | Typical case |
| 3+ | Poor mixing or large line |

---

## 6. Limitations

| Issue | Impact |
|-------|--------|
| **Ideal gas for H₂** | `ig.H2` is ideal gas — adequate for concentration calculations since H₂ is near-ideal at these conditions (1.5 bar, 30 °C) |
| **Mixing efficiency** | The discrete mixing model $(1-\eta)^N$ is a simplification. Real purge fronts are not perfectly step-change or exponential. |
| **Pipe geometry** | Dead legs, valves, and instruments create stagnant zones not captured by the single-volume model |
| **Isothermal assumption** | The JT cooling calculation assumes no heat gain from pipe walls. In practice, the pipe will warm the gas somewhat. |
| **No H₂-N₂ mixing model** | Properties of the H₂-N₂ mixture during the transition are approximated — the endpoint (pure N₂) is accurate |

---

## 7. Plots

| # | File | Content |
|:-|------|---------|
| 1 | `n2_purge_jt_coefficient.png` | $\mu_{JT}$ of N₂ vs T at 200, 3, and 1.5 bar |
| 2 | `n2_purge_temperature_drop.png` | Temperature through expansion stages with cumulative ΔT |
| 3 | `n2_purge_concentration_decay.png` | H₂ concentration decay (semi-log) for $η = 0.3$–$1.0$ |
| 4 | `n2_purge_time_consumption.png` | Purge time and N₂ consumption vs efficiency |
| 5 | `n2_purge_sensitivity.png` | Contour: purge time vs line volume and efficiency |
| 6 | `n2_purge_safety_envelope.png` | Safety zones with concentration decay curves |

---

## 8. References

- NFPA 86: Standard for Ovens and Furnaces (purge requirements)
- API 2009: Safe Welding, Cutting, and Hot Work Practices
- Perry's Chemical Engineers' Handbook, 9th Ed.: Section 27 — Safety
- PYroMat Handbook: Chapter 8 — Multi-Phase Model (mp1) for N₂ properties
