#!/usr/bin/env python3
"""
Generate 100 new computational math and science LaTeX templates with PythonTeX.
Each template has 300-400 lines, topic-specific computations, 6-9 plots, and tables.
"""

import os

BASE_DIR = "/home/user/latex-templates/templates"

def write_template(category, filename, content):
    """Write a template file to the appropriate category directory."""
    filepath = os.path.join(BASE_DIR, category, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Created: {filepath}")

# Template 1: Room Acoustics
room_acoustics = r'''% Room Acoustics Analysis with PythonTeX
% Reverberation time, RT60, Sabine equation computations
\documentclass[11pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{siunitx}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{pythontex}
\usepackage{hyperref}
\usepackage{float}

\title{Room Acoustics Analysis\\Reverberation and Sound Field Modeling}
\author{Acoustics Engineering Laboratory}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
This technical report presents computational analysis of room acoustics including reverberation time calculations using Sabine and Eyring equations, sound absorption modeling, and acoustic parameter optimization for various room configurations.
\end{abstract}

\section{Introduction}

Room acoustics fundamentally determines the quality of sound perception in enclosed spaces. The reverberation time $T_{60}$, defined as the time required for sound to decay by 60 dB, is the primary metric for acoustic characterization.

\begin{pycode}
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import minimize_scalar

# Configure matplotlib for LaTeX
plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10

# Room parameters
room_length = 15.0  # meters
room_width = 10.0   # meters
room_height = 4.0   # meters
room_volume = room_length * room_width * room_height

# Surface areas
floor_area = room_length * room_width
ceiling_area = floor_area
wall_area_long = 2 * room_length * room_height
wall_area_short = 2 * room_width * room_height
total_surface = floor_area + ceiling_area + wall_area_long + wall_area_short

# Speed of sound
c = 343  # m/s at 20°C
\end{pycode}

\section{Room Geometry and Parameters}

The rectangular room under analysis has dimensions:
\begin{itemize}
    \item Length: $L = \py{room_length}$ m
    \item Width: $W = \py{room_width}$ m
    \item Height: $H = \py{room_height}$ m
    \item Volume: $V = \py{room_volume}$ m$^3$
    \item Total Surface Area: $S = \py{round(total_surface, 1)}$ m$^2$
\end{itemize}

\begin{pycode}
# Absorption coefficients for different materials at various frequencies
frequencies = np.array([125, 250, 500, 1000, 2000, 4000])

# Material absorption coefficients
materials = {
    'Concrete': np.array([0.01, 0.01, 0.02, 0.02, 0.02, 0.03]),
    'Carpet': np.array([0.08, 0.24, 0.57, 0.69, 0.71, 0.73]),
    'Acoustic Tiles': np.array([0.29, 0.44, 0.60, 0.77, 0.86, 0.84]),
    'Glass': np.array([0.35, 0.25, 0.18, 0.12, 0.07, 0.04]),
    'Curtains': np.array([0.03, 0.04, 0.11, 0.17, 0.24, 0.35]),
    'Plywood': np.array([0.28, 0.22, 0.17, 0.09, 0.10, 0.11])
}

# Plot absorption coefficients
fig, ax = plt.subplots(figsize=(8, 5))
for material, alpha in materials.items():
    ax.semilogx(frequencies, alpha, 'o-', label=material, linewidth=1.5, markersize=6)
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Absorption Coefficient $\\alpha$')
ax.set_title('Sound Absorption Coefficients for Various Materials')
ax.legend(loc='upper right', fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_xlim([100, 5000])
ax.set_ylim([0, 1])
plt.tight_layout()
plt.savefig('absorption_coefficients.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{absorption_coefficients.pdf}
\caption{Frequency-dependent absorption coefficients for common acoustic materials.}
\label{fig:absorption}
\end{figure}

\section{Sabine Reverberation Time}

The Sabine equation for reverberation time is:
\begin{equation}
T_{60} = \frac{0.161 V}{A}
\label{eq:sabine}
\end{equation}
where $A = \sum_i S_i \alpha_i$ is the total absorption in Sabins.

\begin{pycode}
# Room configuration: concrete walls, carpet floor, acoustic tile ceiling
alpha_walls = materials['Concrete']
alpha_floor = materials['Carpet']
alpha_ceiling = materials['Acoustic Tiles']

# Calculate total absorption at each frequency
total_absorption = (wall_area_long + wall_area_short) * alpha_walls + \
                   floor_area * alpha_floor + \
                   ceiling_area * alpha_ceiling

# Sabine reverberation time
RT60_sabine = 0.161 * room_volume / total_absorption

# Plot RT60 vs frequency
fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogx(frequencies, RT60_sabine, 'b-o', linewidth=2, markersize=8, label='Sabine $T_{60}$')
ax.axhline(y=0.5, color='g', linestyle='--', label='Optimal (Speech)')
ax.axhline(y=1.5, color='r', linestyle='--', label='Optimal (Music)')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Reverberation Time $T_{60}$ (s)')
ax.set_title('Sabine Reverberation Time vs Frequency')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim([100, 5000])
plt.tight_layout()
plt.savefig('rt60_sabine.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{rt60_sabine.pdf}
\caption{Sabine reverberation time across frequency bands with optimal ranges for speech and music.}
\label{fig:rt60_sabine}
\end{figure}

\section{Eyring Reverberation Time}

For rooms with higher absorption, the Eyring formula provides better accuracy:
\begin{equation}
T_{60} = \frac{0.161 V}{-S \ln(1 - \bar{\alpha})}
\label{eq:eyring}
\end{equation}
where $\bar{\alpha}$ is the average absorption coefficient.

\begin{pycode}
# Average absorption coefficient
alpha_avg = total_absorption / total_surface

# Eyring reverberation time
RT60_eyring = 0.161 * room_volume / (-total_surface * np.log(1 - alpha_avg))

# Compare Sabine and Eyring
fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogx(frequencies, RT60_sabine, 'b-o', linewidth=2, markersize=7, label='Sabine')
ax.semilogx(frequencies, RT60_eyring, 'r-s', linewidth=2, markersize=7, label='Eyring')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Reverberation Time $T_{60}$ (s)')
ax.set_title('Comparison of Sabine and Eyring $T_{60}$ Predictions')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim([100, 5000])
plt.tight_layout()
plt.savefig('rt60_comparison.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{rt60_comparison.pdf}
\caption{Comparison of Sabine and Eyring reverberation time predictions.}
\label{fig:rt60_compare}
\end{figure}

\section{Sound Pressure Level Distribution}

The steady-state sound pressure level in a room combines direct and reverberant fields:
\begin{equation}
L_p = L_W + 10 \log_{10}\left(\frac{Q}{4\pi r^2} + \frac{4}{R}\right)
\label{eq:spl}
\end{equation}
where $R = A/(1-\bar{\alpha})$ is the room constant and $Q$ is source directivity.

\begin{pycode}
# Room constant at 1 kHz
idx_1k = 3  # Index for 1000 Hz
A_1k = total_absorption[idx_1k]
alpha_avg_1k = alpha_avg[idx_1k]
R_room = A_1k / (1 - alpha_avg_1k)

# Sound source parameters
L_W = 90  # Sound power level in dB
Q = 2     # Directivity factor (hemispherical)

# Distance from source
r = np.linspace(0.5, 15, 100)

# SPL calculation
direct_field = Q / (4 * np.pi * r**2)
reverb_field = 4 / R_room
L_p = L_W + 10 * np.log10(direct_field + reverb_field)
L_p_direct = L_W + 10 * np.log10(direct_field)
L_p_reverb = L_W + 10 * np.log10(reverb_field) * np.ones_like(r)

# Critical distance
r_c = np.sqrt(Q * R_room / (16 * np.pi))

# Plot SPL distribution
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(r, L_p, 'b-', linewidth=2, label='Total SPL')
ax.plot(r, L_p_direct, 'g--', linewidth=1.5, label='Direct Field')
ax.axhline(y=L_p_reverb[0], color='r', linestyle=':', label='Reverberant Field')
ax.axvline(x=r_c, color='k', linestyle='--', alpha=0.7, label=f'$r_c$ = {r_c:.2f} m')
ax.set_xlabel('Distance from Source (m)')
ax.set_ylabel('Sound Pressure Level (dB)')
ax.set_title('Sound Pressure Level Distribution in Room')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim([0, 15])
plt.tight_layout()
plt.savefig('spl_distribution.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{spl_distribution.pdf}
\caption{Sound pressure level as function of distance showing direct and reverberant field contributions.}
\label{fig:spl}
\end{figure}

The critical distance $r_c = \py{round(r_c, 2)}$ m marks the transition between direct and reverberant field dominance.

\section{Room Mode Analysis}

The room modes (standing wave frequencies) are given by:
\begin{equation}
f_{n_x, n_y, n_z} = \frac{c}{2}\sqrt{\left(\frac{n_x}{L}\right)^2 + \left(\frac{n_y}{W}\right)^2 + \left(\frac{n_z}{H}\right)^2}
\label{eq:modes}
\end{equation}

\begin{pycode}
# Calculate room modes up to 200 Hz
modes = []
for nx in range(0, 5):
    for ny in range(0, 5):
        for nz in range(0, 5):
            if nx == 0 and ny == 0 and nz == 0:
                continue
            f = (c/2) * np.sqrt((nx/room_length)**2 + (ny/room_width)**2 + (nz/room_height)**2)
            if f <= 200:
                modes.append((f, nx, ny, nz))

modes.sort(key=lambda x: x[0])

# Plot mode distribution
fig, ax = plt.subplots(figsize=(10, 4))
freqs = [m[0] for m in modes]
ax.eventplot([freqs], lineoffsets=0.5, linelengths=0.8, colors='blue')
ax.set_xlabel('Frequency (Hz)')
ax.set_title('Room Mode Distribution (0-200 Hz)')
ax.set_xlim([0, 200])
ax.set_ylim([0, 1])
ax.set_yticks([])
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('room_modes.pdf', dpi=150, bbox_inches='tight')
plt.close()

# Schroeder frequency
N_modes = len(modes)
f_schroeder = 2000 * np.sqrt(RT60_sabine[idx_1k] / room_volume)
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{room_modes.pdf}
\caption{Distribution of room modes in the low-frequency range.}
\label{fig:modes}
\end{figure}

The Schroeder frequency $f_s = \py{round(f_schroeder, 1)}$ Hz marks the transition to statistical acoustics.

\section{Clarity and Definition Indices}

Speech intelligibility metrics include the Clarity Index $C_{50}$:
\begin{equation}
C_{50} = 10 \log_{10}\left(\frac{\int_0^{50\text{ms}} p^2(t)\,dt}{\int_{50\text{ms}}^{\infty} p^2(t)\,dt}\right)
\label{eq:clarity}
\end{equation}

\begin{pycode}
# Simulate impulse response decay
t_ir = np.linspace(0, 2, 1000)
decay_rate = 6.91 / RT60_sabine[idx_1k]  # From RT60 definition
impulse_response = np.exp(-decay_rate * t_ir)

# Calculate C50 and C80
t_50ms = 0.050
t_80ms = 0.080
idx_50 = np.argmin(np.abs(t_ir - t_50ms))
idx_80 = np.argmin(np.abs(t_ir - t_80ms))

energy_early_50 = np.trapz(impulse_response[:idx_50]**2, t_ir[:idx_50])
energy_late_50 = np.trapz(impulse_response[idx_50:]**2, t_ir[idx_50:])
C50 = 10 * np.log10(energy_early_50 / energy_late_50)

energy_early_80 = np.trapz(impulse_response[:idx_80]**2, t_ir[:idx_80])
energy_late_80 = np.trapz(impulse_response[idx_80:]**2, t_ir[idx_80:])
C80 = 10 * np.log10(energy_early_80 / energy_late_80)

# Definition D50
D50 = energy_early_50 / (energy_early_50 + energy_late_50)

# Plot impulse response
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(t_ir * 1000, 20*np.log10(impulse_response + 1e-10), 'b-', linewidth=1.5)
ax.axvline(x=50, color='g', linestyle='--', label='50 ms (Speech)')
ax.axvline(x=80, color='r', linestyle='--', label='80 ms (Music)')
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Level (dB)')
ax.set_title('Room Impulse Response Energy Decay')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim([0, 500])
ax.set_ylim([-60, 5])
plt.tight_layout()
plt.savefig('impulse_response.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{impulse_response.pdf}
\caption{Room impulse response energy decay curve with early time limits.}
\label{fig:impulse}
\end{figure}

\section{Acoustic Treatment Optimization}

\begin{pycode}
# Vary ceiling absorption to optimize RT60
ceiling_coverage = np.linspace(0, 1, 50)  # Fraction of ceiling with treatment
RT60_optimized = []

for coverage in ceiling_coverage:
    alpha_ceiling_opt = coverage * materials['Acoustic Tiles'] + \
                        (1 - coverage) * materials['Concrete']
    A_opt = (wall_area_long + wall_area_short) * alpha_walls + \
            floor_area * alpha_floor + \
            ceiling_area * alpha_ceiling_opt
    RT60_opt = 0.161 * room_volume / A_opt[idx_1k]
    RT60_optimized.append(RT60_opt)

RT60_optimized = np.array(RT60_optimized)

# Find optimal coverage for target RT60
target_RT60 = 0.8  # Target for multipurpose room
optimal_idx = np.argmin(np.abs(RT60_optimized - target_RT60))
optimal_coverage = ceiling_coverage[optimal_idx]

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(ceiling_coverage * 100, RT60_optimized, 'b-', linewidth=2)
ax.axhline(y=target_RT60, color='r', linestyle='--', label=f'Target $T_{{60}}$ = {target_RT60} s')
ax.axvline(x=optimal_coverage * 100, color='g', linestyle=':',
           label=f'Optimal = {optimal_coverage*100:.1f}\\%')
ax.set_xlabel('Acoustic Tile Coverage (\\%)')
ax.set_ylabel('Reverberation Time $T_{60}$ (s)')
ax.set_title('$T_{60}$ Optimization via Ceiling Treatment')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('rt60_optimization.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{rt60_optimization.pdf}
\caption{Optimization of $T_{60}$ by varying acoustic ceiling tile coverage.}
\label{fig:optimization}
\end{figure}

For a target $T_{60} = \py{target_RT60}$ s, the optimal ceiling coverage is $\py{round(optimal_coverage * 100, 1)}\%$.

\section{Results Summary}

\begin{pycode}
# Create results table
results_data = [
    ['125', f'{RT60_sabine[0]:.2f}', f'{RT60_eyring[0]:.2f}', f'{total_absorption[0]:.1f}'],
    ['250', f'{RT60_sabine[1]:.2f}', f'{RT60_eyring[1]:.2f}', f'{total_absorption[1]:.1f}'],
    ['500', f'{RT60_sabine[2]:.2f}', f'{RT60_eyring[2]:.2f}', f'{total_absorption[2]:.1f}'],
    ['1000', f'{RT60_sabine[3]:.2f}', f'{RT60_eyring[3]:.2f}', f'{total_absorption[3]:.1f}'],
    ['2000', f'{RT60_sabine[4]:.2f}', f'{RT60_eyring[4]:.2f}', f'{total_absorption[4]:.1f}'],
    ['4000', f'{RT60_sabine[5]:.2f}', f'{RT60_eyring[5]:.2f}', f'{total_absorption[5]:.1f}'],
]

print(r'\begin{table}[H]')
print(r'\centering')
print(r'\caption{Summary of Room Acoustic Parameters}')
print(r'\begin{tabular}{@{}cccc@{}}')
print(r'\toprule')
print(r'Frequency (Hz) & $T_{60}$ Sabine (s) & $T_{60}$ Eyring (s) & Total Absorption (Sabins) \\')
print(r'\midrule')
for row in results_data:
    print(' & '.join(row) + r' \\')
print(r'\bottomrule')
print(r'\end{tabular}')
print(r'\label{tab:results}')
print(r'\end{table}')
\end{pycode}

Additional acoustic metrics at 1 kHz:
\begin{itemize}
    \item Critical Distance: $r_c = \py{round(r_c, 2)}$ m
    \item Clarity Index: $C_{50} = \py{round(C50, 1)}$ dB
    \item Music Clarity: $C_{80} = \py{round(C80, 1)}$ dB
    \item Definition: $D_{50} = \py{round(D50 * 100, 1)}\%$
    \item Room Constant: $R = \py{round(R_room, 1)}$ m$^2$
\end{itemize}

\section{Conclusions}

The room acoustic analysis demonstrates that the current configuration with carpet flooring and acoustic tile ceiling provides acceptable reverberation times for multipurpose use. The Schroeder frequency of \py{round(f_schroeder, 1)} Hz indicates reliable statistical acoustic behavior above this frequency. Optimization studies show that \py{round(optimal_coverage * 100, 0)}\% ceiling treatment achieves the target $T_{60}$ of \py{target_RT60} seconds.

\end{document}
'''

# Template 2: Sound Propagation
sound_propagation = r'''% Sound Propagation Analysis with PythonTeX
% Wave equation, impedance, transmission loss computations
\documentclass[11pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{siunitx}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{pythontex}
\usepackage{hyperref}
\usepackage{float}

\title{Sound Propagation Analysis\\Wave Equations and Transmission Loss}
\author{Acoustic Engineering Department}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
This report analyzes sound wave propagation through various media, including calculations of acoustic impedance, transmission and reflection coefficients, and transmission loss through partitions using mass law and coincidence effects.
\end{abstract}

\section{Introduction}

Sound propagation in fluids and through structures is governed by the acoustic wave equation and boundary conditions at material interfaces. Understanding these phenomena is essential for noise control engineering.

\begin{pycode}
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import jv, hankel1

# Configure matplotlib for LaTeX
plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10

# Physical constants
c_air = 343  # Speed of sound in air (m/s)
rho_air = 1.21  # Air density (kg/m³)
Z_air = rho_air * c_air  # Acoustic impedance of air

# Other media properties
media = {
    'Air': {'c': 343, 'rho': 1.21},
    'Water': {'c': 1480, 'rho': 1000},
    'Steel': {'c': 5960, 'rho': 7850},
    'Concrete': {'c': 3400, 'rho': 2400},
    'Glass': {'c': 5200, 'rho': 2500},
    'Wood': {'c': 3800, 'rho': 600}
}

# Calculate impedances
for name, props in media.items():
    props['Z'] = props['rho'] * props['c']
\end{pycode}

\section{Acoustic Impedance}

The characteristic acoustic impedance of a medium is:
\begin{equation}
Z = \rho c
\label{eq:impedance}
\end{equation}

\begin{pycode}
# Plot impedance comparison
fig, ax = plt.subplots(figsize=(10, 5))
names = list(media.keys())
impedances = [media[n]['Z'] for n in names]
colors = plt.cm.viridis(np.linspace(0, 0.8, len(names)))

bars = ax.bar(names, impedances, color=colors, edgecolor='black')
ax.set_ylabel('Acoustic Impedance (Pa$\\cdot$s/m)')
ax.set_title('Characteristic Acoustic Impedance of Various Media')
ax.set_yscale('log')
ax.grid(True, alpha=0.3, axis='y')

# Add value labels
for bar, val in zip(bars, impedances):
    ax.text(bar.get_x() + bar.get_width()/2, val * 1.1, f'{val:.0f}',
            ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig('impedance_comparison.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{impedance_comparison.pdf}
\caption{Acoustic impedance comparison across different media.}
\label{fig:impedance}
\end{figure}

\section{Reflection and Transmission at Interfaces}

At the interface between two media, the pressure reflection coefficient is:
\begin{equation}
R = \frac{Z_2 - Z_1}{Z_2 + Z_1}
\label{eq:reflection}
\end{equation}

\begin{pycode}
# Calculate reflection coefficients for air-to-material interfaces
materials = ['Water', 'Steel', 'Concrete', 'Glass', 'Wood']
Z1 = media['Air']['Z']
R_coeffs = []
T_coeffs = []

for mat in materials:
    Z2 = media[mat]['Z']
    R = (Z2 - Z1) / (Z2 + Z1)
    T = 2 * Z2 / (Z2 + Z1)
    R_coeffs.append(R)
    T_coeffs.append(T)

# Plot coefficients
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.bar(materials, R_coeffs, color='steelblue', edgecolor='black')
ax1.set_ylabel('Pressure Reflection Coefficient $R$')
ax1.set_title('Reflection at Air-Material Interface')
ax1.axhline(y=0, color='k', linewidth=0.5)
ax1.grid(True, alpha=0.3, axis='y')

# Intensity transmission
T_intensity = [1 - r**2 for r in R_coeffs]
ax2.bar(materials, T_intensity, color='coral', edgecolor='black')
ax2.set_ylabel('Intensity Transmission Coefficient $T_I$')
ax2.set_title('Intensity Transmission at Air-Material Interface')
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('reflection_transmission.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{reflection_transmission.pdf}
\caption{Reflection and transmission coefficients at air-material interfaces.}
\label{fig:reflection}
\end{figure}

\section{Mass Law Transmission Loss}

The mass law describes transmission loss through a partition:
\begin{equation}
TL = 20 \log_{10}(\pi f m / \rho c) = 20 \log_{10}(f) + 20 \log_{10}(m) - 42.5
\label{eq:masslaw}
\end{equation}
where $m$ is the surface mass density (kg/m$^2$).

\begin{pycode}
# Frequency range
freq = np.logspace(1, 4, 200)  # 10 Hz to 10 kHz

# Different partition surface mass densities
surface_masses = {
    'Gypsum Board (12mm)': 10,
    'Plywood (18mm)': 11,
    'Concrete (100mm)': 240,
    'Steel (3mm)': 24,
    'Glass (6mm)': 15
}

# Calculate transmission loss
fig, ax = plt.subplots(figsize=(10, 6))

for name, m in surface_masses.items():
    TL = 20 * np.log10(np.pi * freq * m / (rho_air * c_air))
    ax.semilogx(freq, TL, linewidth=1.5, label=f'{name} ({m} kg/m$^2$)')

ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Transmission Loss (dB)')
ax.set_title('Mass Law Transmission Loss for Various Partitions')
ax.legend(loc='lower right', fontsize=9)
ax.grid(True, alpha=0.3, which='both')
ax.set_xlim([10, 10000])
ax.set_ylim([0, 80])
plt.tight_layout()
plt.savefig('mass_law_tl.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{mass_law_tl.pdf}
\caption{Mass law transmission loss predictions for different partition types.}
\label{fig:masslaw}
\end{figure}

\section{Coincidence Effect}

The coincidence frequency where bending wave speed equals trace wave speed:
\begin{equation}
f_c = \frac{c^2}{2\pi} \sqrt{\frac{12\rho(1-\nu^2)}{E h^2}}
\label{eq:coincidence}
\end{equation}

\begin{pycode}
# Panel properties for coincidence calculation
panels = {
    'Steel (3mm)': {'E': 200e9, 'rho': 7850, 'nu': 0.3, 'h': 0.003},
    'Aluminum (2mm)': {'E': 70e9, 'rho': 2700, 'nu': 0.33, 'h': 0.002},
    'Glass (6mm)': {'E': 70e9, 'rho': 2500, 'nu': 0.22, 'h': 0.006},
    'Plywood (18mm)': {'E': 12e9, 'rho': 600, 'nu': 0.3, 'h': 0.018}
}

# Calculate coincidence frequencies
f_coincidence = {}
for name, props in panels.items():
    fc = (c_air**2 / (2 * np.pi)) * np.sqrt(12 * props['rho'] * (1 - props['nu']**2) /
                                            (props['E'] * props['h']**2))
    f_coincidence[name] = fc

# Plot TL with coincidence dip
fig, ax = plt.subplots(figsize=(10, 6))

for name, props in panels.items():
    m = props['rho'] * props['h']
    fc = f_coincidence[name]

    # Mass law
    TL_mass = 20 * np.log10(np.pi * freq * m / (rho_air * c_air))

    # Add coincidence dip (simplified model)
    dip_width = fc * 0.5
    coincidence_dip = 15 * np.exp(-(freq - fc)**2 / (2 * (dip_width)**2))
    TL = TL_mass - coincidence_dip
    TL = np.maximum(TL, 0)

    ax.semilogx(freq, TL, linewidth=1.5, label=f'{name}')
    ax.axvline(x=fc, linestyle=':', alpha=0.5)

ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Transmission Loss (dB)')
ax.set_title('Transmission Loss with Coincidence Effect')
ax.legend(loc='lower right', fontsize=9)
ax.grid(True, alpha=0.3, which='both')
ax.set_xlim([100, 10000])
ax.set_ylim([0, 60])
plt.tight_layout()
plt.savefig('coincidence_tl.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{coincidence_tl.pdf}
\caption{Transmission loss showing coincidence frequency dips.}
\label{fig:coincidence}
\end{figure}

\section{Double Wall Transmission Loss}

Double wall construction improves transmission loss at frequencies above the mass-air-mass resonance:
\begin{equation}
f_0 = \frac{1}{2\pi}\sqrt{\frac{\rho c^2}{\ell}\left(\frac{1}{m_1} + \frac{1}{m_2}\right)}
\label{eq:mam_resonance}
\end{equation}

\begin{pycode}
# Double wall parameters
m1 = 12  # First leaf mass (kg/m²)
m2 = 12  # Second leaf mass (kg/m²)
air_gaps = [50, 100, 200]  # mm

fig, ax = plt.subplots(figsize=(10, 6))

for gap in air_gaps:
    ell = gap / 1000  # Convert to meters

    # Mass-air-mass resonance frequency
    f0 = (1 / (2 * np.pi)) * np.sqrt((rho_air * c_air**2 / ell) * (1/m1 + 1/m2))

    # Calculate double wall TL
    TL_double = np.zeros_like(freq)

    for i, f in enumerate(freq):
        if f < f0:
            # Below resonance - mass law of total mass
            TL_double[i] = 20 * np.log10(np.pi * f * (m1 + m2) / (rho_air * c_air))
        else:
            # Above resonance - 18 dB/octave
            TL_single = 20 * np.log10(np.pi * f * m1 / (rho_air * c_air))
            TL_double[i] = 2 * TL_single + 20 * np.log10(f / f0)

    TL_double = np.maximum(TL_double, 0)
    ax.semilogx(freq, TL_double, linewidth=1.5, label=f'Gap = {gap} mm')

# Single wall reference
TL_single = 20 * np.log10(np.pi * freq * (m1 + m2) / (rho_air * c_air))
ax.semilogx(freq, TL_single, 'k--', linewidth=1, label='Single wall (same mass)')

ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Transmission Loss (dB)')
ax.set_title('Double Wall Transmission Loss vs Air Gap')
ax.legend(loc='lower right')
ax.grid(True, alpha=0.3, which='both')
ax.set_xlim([50, 5000])
ax.set_ylim([0, 80])
plt.tight_layout()
plt.savefig('double_wall_tl.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{double_wall_tl.pdf}
\caption{Double wall transmission loss for various air gap widths.}
\label{fig:doublewall}
\end{figure}

\section{Atmospheric Absorption}

Sound attenuation in air due to molecular relaxation:
\begin{equation}
\alpha = \alpha_0 + \alpha_{rot} + \alpha_{vib,O} + \alpha_{vib,N}
\label{eq:atmospheric}
\end{equation}

\begin{pycode}
# Atmospheric absorption calculation (ISO 9613-1 simplified)
def atmospheric_absorption(f, T, h, p):
    """Calculate atmospheric absorption coefficient in dB/m."""
    # Temperature in Kelvin
    T_K = T + 273.15
    T_ref = 293.15
    p_ref = 101.325

    # Molar concentration of water vapor
    C = -6.8346 * (273.16/T_K)**1.261 + 4.6151
    h_molar = h * (p_ref/p) * 10**C

    # Relaxation frequencies
    f_rO = (p/p_ref) * (24 + 4.04e4 * h_molar * (0.02 + h_molar)/(0.391 + h_molar))
    f_rN = (p/p_ref) * (T_K/T_ref)**(-0.5) * (9 + 280 * h_molar *
           np.exp(-4.170 * ((T_K/T_ref)**(-1/3) - 1)))

    # Absorption coefficient (dB/m)
    alpha = 8.686 * f**2 * ((1.84e-11 * (p_ref/p) * (T_K/T_ref)**0.5) +
            (T_K/T_ref)**(-2.5) * (0.01275 * np.exp(-2239.1/T_K) / (f_rO + f**2/f_rO) +
            0.1068 * np.exp(-3352.0/T_K) / (f_rN + f**2/f_rN)))
    return alpha

# Calculate for different conditions
freq_atm = np.logspace(2, 4.5, 100)
conditions = [
    {'T': 20, 'h': 50, 'p': 101.325, 'label': '20°C, 50\\% RH'},
    {'T': 20, 'h': 20, 'p': 101.325, 'label': '20°C, 20\\% RH'},
    {'T': 0, 'h': 50, 'p': 101.325, 'label': '0°C, 50\\% RH'},
]

fig, ax = plt.subplots(figsize=(10, 6))

for cond in conditions:
    alpha = atmospheric_absorption(freq_atm, cond['T'], cond['h'], cond['p'])
    ax.loglog(freq_atm, alpha * 1000, linewidth=1.5, label=cond['label'])

ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Absorption Coefficient (dB/km)')
ax.set_title('Atmospheric Sound Absorption')
ax.legend()
ax.grid(True, alpha=0.3, which='both')
ax.set_xlim([100, 30000])
plt.tight_layout()
plt.savefig('atmospheric_absorption.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{atmospheric_absorption.pdf}
\caption{Atmospheric sound absorption for different temperature and humidity conditions.}
\label{fig:atmospheric}
\end{figure}

\section{Spherical Wave Spreading}

Sound pressure decreases with distance from a point source:
\begin{equation}
L_p(r) = L_W - 20\log_{10}(r) - 11
\label{eq:spreading}
\end{equation}

\begin{pycode}
# Source power and distance
L_W = 100  # Sound power level (dB)
distances = np.linspace(1, 100, 100)

# Different frequency cases with atmospheric absorption
freq_cases = [500, 2000, 8000]  # Hz
T, h, p = 20, 50, 101.325

fig, ax = plt.subplots(figsize=(10, 6))

for f in freq_cases:
    alpha = atmospheric_absorption(f, T, h, p)
    L_p = L_W - 20 * np.log10(distances) - 11 - alpha * distances
    ax.plot(distances, L_p, linewidth=1.5, label=f'{f} Hz')

# Geometric spreading only
L_p_geo = L_W - 20 * np.log10(distances) - 11
ax.plot(distances, L_p_geo, 'k--', linewidth=1, label='Geometric only')

ax.set_xlabel('Distance (m)')
ax.set_ylabel('Sound Pressure Level (dB)')
ax.set_title('Sound Level vs Distance with Atmospheric Absorption')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim([1, 100])
plt.tight_layout()
plt.savefig('spreading_loss.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{spreading_loss.pdf}
\caption{Sound pressure level decay with distance including atmospheric absorption.}
\label{fig:spreading}
\end{figure}

\section{Results Summary}

\begin{pycode}
# Create summary table
print(r'\begin{table}[H]')
print(r'\centering')
print(r'\caption{Summary of Acoustic Properties}')
print(r'\begin{tabular}{@{}lccc@{}}')
print(r'\toprule')
print(r'Material & $c$ (m/s) & $\rho$ (kg/m$^3$) & $Z$ (Pa$\cdot$s/m) \\')
print(r'\midrule')
for name, props in media.items():
    print(f"{name} & {props['c']} & {props['rho']} & {props['Z']:.0f} \\\\")
print(r'\bottomrule')
print(r'\end{tabular}')
print(r'\label{tab:properties}')
print(r'\end{table}')

# Coincidence frequencies table
print(r'\begin{table}[H]')
print(r'\centering')
print(r'\caption{Coincidence Frequencies}')
print(r'\begin{tabular}{@{}lc@{}}')
print(r'\toprule')
print(r'Panel Type & $f_c$ (Hz) \\')
print(r'\midrule')
for name, fc in f_coincidence.items():
    print(f"{name} & {fc:.0f} \\\\")
print(r'\bottomrule')
print(r'\end{tabular}')
print(r'\label{tab:coincidence}')
print(r'\end{table}')
\end{pycode}

\section{Conclusions}

This analysis demonstrates the key principles of sound propagation and transmission loss. The mass law provides a baseline for partition design, while coincidence effects and double-wall construction significantly influence the achievable sound insulation. Atmospheric absorption becomes critical for outdoor sound propagation at high frequencies and long distances.

\end{document}
'''

# Template 3: Musical Acoustics
musical_acoustics = r'''% Musical Acoustics Analysis with PythonTeX
% Harmonics, resonance, instrument modeling
\documentclass[11pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{siunitx}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{pythontex}
\usepackage{hyperref}
\usepackage{float}

\title{Musical Acoustics\\Harmonic Analysis and Instrument Modeling}
\author{Music Technology Laboratory}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
This report presents computational analysis of musical acoustics including harmonic series generation, string vibration modes, wind instrument resonances, and psychoacoustic phenomena such as beating and combination tones.
\end{abstract}

\section{Introduction}

Musical instruments produce sound through vibrating systems that generate harmonic spectra. Understanding these vibrations and their acoustic properties is fundamental to instrument design and music technology.

\begin{pycode}
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fft import fft, fftfreq
from scipy.signal import sawtooth, square

# Configure matplotlib for LaTeX
plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10

# Physical constants
c = 343  # Speed of sound in air (m/s)

# Musical note frequencies (Equal temperament, A4 = 440 Hz)
def note_frequency(note_number):
    """Calculate frequency for MIDI note number (A4 = 69)."""
    return 440 * 2**((note_number - 69) / 12)

# Note names
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
\end{pycode}

\section{Harmonic Series}

A vibrating system produces harmonics at integer multiples of the fundamental:
\begin{equation}
f_n = n f_1, \quad n = 1, 2, 3, \ldots
\label{eq:harmonics}
\end{equation}

\begin{pycode}
# Generate harmonic series for A2 (110 Hz)
f1 = 110  # Fundamental frequency
n_harmonics = 16
harmonics = np.arange(1, n_harmonics + 1) * f1

# Map to musical notes
fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(range(1, n_harmonics + 1), harmonics, color='steelblue', edgecolor='black')
ax.set_xlabel('Harmonic Number')
ax.set_ylabel('Frequency (Hz)')
ax.set_title(f'Harmonic Series of A2 ({f1} Hz)')
ax.set_xticks(range(1, n_harmonics + 1))
ax.grid(True, alpha=0.3, axis='y')

# Add frequency labels
for i, f in enumerate(harmonics):
    ax.text(i + 1, f + 20, f'{f:.0f}', ha='center', fontsize=7)

plt.tight_layout()
plt.savefig('harmonic_series.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{harmonic_series.pdf}
\caption{Harmonic series frequencies for a fundamental of 110 Hz (A2).}
\label{fig:harmonics}
\end{figure}

\section{String Vibration Modes}

The frequencies of an ideal vibrating string are:
\begin{equation}
f_n = \frac{n}{2L}\sqrt{\frac{T}{\mu}}
\label{eq:string}
\end{equation}
where $L$ is length, $T$ is tension, and $\mu$ is linear mass density.

\begin{pycode}
# Guitar string parameters (E2 string)
L = 0.65  # Scale length (m)
T = 70  # Tension (N)
mu = 0.00531  # Linear density (kg/m) for 0.046" steel string

# Fundamental frequency
f1_string = (1 / (2 * L)) * np.sqrt(T / mu)

# Calculate mode shapes
x = np.linspace(0, L, 500)
modes = [1, 2, 3, 4, 5]

fig, axes = plt.subplots(len(modes), 1, figsize=(10, 8), sharex=True)

for ax, n in zip(axes, modes):
    y = np.sin(n * np.pi * x / L)
    ax.plot(x * 100, y, 'b-', linewidth=1.5)
    ax.fill_between(x * 100, y, alpha=0.3)
    ax.set_ylabel(f'Mode {n}', fontsize=9)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.set_ylim([-1.3, 1.3])
    ax.grid(True, alpha=0.3)
    fn = n * f1_string
    ax.text(0.98, 0.85, f'$f_{n}$ = {fn:.1f} Hz', transform=ax.transAxes,
            ha='right', fontsize=9)

axes[-1].set_xlabel('Position along string (cm)')
fig.suptitle('String Vibration Mode Shapes', fontsize=12, y=1.02)
plt.tight_layout()
plt.savefig('string_modes.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{string_modes.pdf}
\caption{Mode shapes for a vibrating guitar string.}
\label{fig:string_modes}
\end{figure}

The calculated fundamental frequency is $f_1 = \py{round(f1_string, 1)}$ Hz.

\section{Waveform Synthesis}

Different timbres result from varying harmonic amplitudes.

\begin{pycode}
# Time array
fs = 44100  # Sample rate
duration = 0.02  # 20 ms
t = np.linspace(0, duration, int(fs * duration))
f0 = 220  # A3

# Generate different waveforms
waveforms = {
    'Sine': np.sin(2 * np.pi * f0 * t),
    'Triangle': sawtooth(2 * np.pi * f0 * t, 0.5),
    'Sawtooth': sawtooth(2 * np.pi * f0 * t),
    'Square': square(2 * np.pi * f0 * t)
}

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()

for ax, (name, wave) in zip(axes, waveforms.items()):
    ax.plot(t * 1000, wave, 'b-', linewidth=1)
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Amplitude')
    ax.set_title(f'{name} Wave')
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, duration * 1000])

plt.tight_layout()
plt.savefig('waveforms.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{waveforms.pdf}
\caption{Different musical waveform types at 220 Hz.}
\label{fig:waveforms}
\end{figure}

\section{Spectral Analysis}

\begin{pycode}
# Generate longer signals for FFT
duration_fft = 0.1
t_fft = np.linspace(0, duration_fft, int(fs * duration_fft))
N = len(t_fft)

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()

waveforms_fft = {
    'Sine': np.sin(2 * np.pi * f0 * t_fft),
    'Triangle': sawtooth(2 * np.pi * f0 * t_fft, 0.5),
    'Sawtooth': sawtooth(2 * np.pi * f0 * t_fft),
    'Square': square(2 * np.pi * f0 * t_fft)
}

for ax, (name, wave) in zip(axes, waveforms_fft.items()):
    # Compute FFT
    yf = np.abs(fft(wave))[:N//2]
    xf = fftfreq(N, 1/fs)[:N//2]

    # Normalize
    yf = yf / np.max(yf)

    ax.plot(xf, yf, 'b-', linewidth=0.8)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Normalized Magnitude')
    ax.set_title(f'{name} Wave Spectrum')
    ax.set_xlim([0, 3000])
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('spectra.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{spectra.pdf}
\caption{Frequency spectra of different waveform types showing harmonic content.}
\label{fig:spectra}
\end{figure}

\section{Wind Instrument Resonances}

Cylindrical pipes have resonances at:
\begin{align}
\text{Open pipe:} \quad f_n &= \frac{nc}{2L} \\
\text{Closed pipe:} \quad f_n &= \frac{(2n-1)c}{4L}
\end{align}

\begin{pycode}
# Pipe parameters
L_pipe = 0.5  # Pipe length (m)

# Open pipe resonances (all harmonics)
n_resonances = 8
f_open = np.array([n * c / (2 * L_pipe) for n in range(1, n_resonances + 1)])

# Closed pipe resonances (odd harmonics only)
f_closed = np.array([(2*n - 1) * c / (4 * L_pipe) for n in range(1, n_resonances + 1)])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Open pipe
ax1.bar(range(1, n_resonances + 1), f_open, color='forestgreen', edgecolor='black')
ax1.set_xlabel('Mode Number')
ax1.set_ylabel('Frequency (Hz)')
ax1.set_title(f'Open Pipe Resonances (L = {L_pipe} m)')
ax1.grid(True, alpha=0.3, axis='y')

# Closed pipe
ax2.bar(range(1, n_resonances + 1), f_closed, color='darkorange', edgecolor='black')
ax2.set_xlabel('Mode Number')
ax2.set_ylabel('Frequency (Hz)')
ax2.set_title(f'Closed Pipe Resonances (L = {L_pipe} m)')
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('pipe_resonances.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{pipe_resonances.pdf}
\caption{Resonance frequencies for open and closed cylindrical pipes.}
\label{fig:pipes}
\end{figure}

\section{Beating Phenomenon}

When two tones of similar frequency are combined:
\begin{equation}
y = A\cos(2\pi f_1 t) + A\cos(2\pi f_2 t) = 2A\cos\left(\pi(f_1-f_2)t\right)\cos\left(\pi(f_1+f_2)t\right)
\label{eq:beating}
\end{equation}

\begin{pycode}
# Beat frequency demonstration
f1_beat = 440  # Hz
f2_beat = 443  # Hz
beat_freq = abs(f1_beat - f2_beat)

duration_beat = 1.0
t_beat = np.linspace(0, duration_beat, int(fs * duration_beat))

y1 = np.cos(2 * np.pi * f1_beat * t_beat)
y2 = np.cos(2 * np.pi * f2_beat * t_beat)
y_sum = y1 + y2

fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

axes[0].plot(t_beat, y1, 'b-', linewidth=0.5)
axes[0].set_ylabel('$f_1$ = 440 Hz')
axes[0].set_title('Beating Between Two Close Frequencies')
axes[0].set_xlim([0, 0.5])

axes[1].plot(t_beat, y2, 'r-', linewidth=0.5)
axes[1].set_ylabel('$f_2$ = 443 Hz')

axes[2].plot(t_beat, y_sum, 'g-', linewidth=0.5)
envelope = 2 * np.cos(np.pi * beat_freq * t_beat)
axes[2].plot(t_beat, envelope, 'k--', linewidth=1, label='Envelope')
axes[2].plot(t_beat, -envelope, 'k--', linewidth=1)
axes[2].set_ylabel('Sum')
axes[2].set_xlabel('Time (s)')
axes[2].legend()

for ax in axes:
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('beating.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{beating.pdf}
\caption{Beating phenomenon with beat frequency of \py{beat_freq} Hz.}
\label{fig:beating}
\end{figure}

\section{Equal Temperament vs Just Intonation}

\begin{pycode}
# Compare tuning systems
intervals = ['Unison', 'Minor 2nd', 'Major 2nd', 'Minor 3rd', 'Major 3rd',
             'Perfect 4th', 'Tritone', 'Perfect 5th', 'Minor 6th', 'Major 6th',
             'Minor 7th', 'Major 7th', 'Octave']

# Equal temperament ratios
equal_temp = [2**(i/12) for i in range(13)]

# Just intonation ratios
just_int = [1, 16/15, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2, 8/5, 5/3, 16/9, 15/8, 2]

# Cents difference
cents_diff = [1200 * np.log2(j/e) if e != 0 else 0 for j, e in zip(just_int, equal_temp)]

fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(intervals))
width = 0.35

bars1 = ax.bar(x - width/2, equal_temp, width, label='Equal Temperament', color='steelblue')
bars2 = ax.bar(x + width/2, just_int, width, label='Just Intonation', color='coral')

ax.set_xlabel('Interval')
ax.set_ylabel('Frequency Ratio')
ax.set_title('Comparison of Tuning Systems')
ax.set_xticks(x)
ax.set_xticklabels(intervals, rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('tuning_comparison.pdf', dpi=150, bbox_inches='tight')
plt.close()

# Cents difference plot
fig, ax = plt.subplots(figsize=(12, 5))
colors = ['green' if c >= 0 else 'red' for c in cents_diff]
ax.bar(intervals, cents_diff, color=colors, edgecolor='black')
ax.set_xlabel('Interval')
ax.set_ylabel('Difference (cents)')
ax.set_title('Just Intonation vs Equal Temperament (cents)')
ax.axhline(y=0, color='k', linewidth=0.5)
plt.xticks(rotation=45, ha='right')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('cents_difference.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{tuning_comparison.pdf}
\caption{Frequency ratios in equal temperament and just intonation.}
\label{fig:tuning}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{cents_difference.pdf}
\caption{Difference between just intonation and equal temperament in cents.}
\label{fig:cents}
\end{figure}

\section{ADSR Envelope}

Musical instruments have characteristic amplitude envelopes:

\begin{pycode}
# ADSR envelope parameters
attack = 0.05  # seconds
decay = 0.1
sustain_level = 0.7
sustain_time = 0.3
release = 0.2

# Generate envelope
t_env = np.linspace(0, attack + decay + sustain_time + release, 1000)
envelope = np.zeros_like(t_env)

for i, t in enumerate(t_env):
    if t < attack:
        envelope[i] = t / attack
    elif t < attack + decay:
        envelope[i] = 1 - (1 - sustain_level) * (t - attack) / decay
    elif t < attack + decay + sustain_time:
        envelope[i] = sustain_level
    else:
        envelope[i] = sustain_level * (1 - (t - attack - decay - sustain_time) / release)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(t_env * 1000, envelope, 'b-', linewidth=2)
ax.axvline(x=attack*1000, color='r', linestyle='--', alpha=0.7, label='Attack')
ax.axvline(x=(attack+decay)*1000, color='g', linestyle='--', alpha=0.7, label='Decay')
ax.axvline(x=(attack+decay+sustain_time)*1000, color='orange', linestyle='--', alpha=0.7, label='Sustain')
ax.fill_between(t_env * 1000, envelope, alpha=0.3)
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Amplitude')
ax.set_title('ADSR Envelope')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim([0, (attack + decay + sustain_time + release) * 1000])
ax.set_ylim([0, 1.1])

plt.tight_layout()
plt.savefig('adsr_envelope.pdf', dpi=150, bbox_inches='tight')
plt.close()
\end{pycode}

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{adsr_envelope.pdf}
\caption{ADSR (Attack-Decay-Sustain-Release) amplitude envelope.}
\label{fig:adsr}
\end{figure}

\section{Results Summary}

\begin{pycode}
# Create results table
print(r'\begin{table}[H]')
print(r'\centering')
print(r'\caption{Musical Interval Frequency Ratios}')
print(r'\begin{tabular}{@{}lccc@{}}')
print(r'\toprule')
print(r'Interval & Equal Temp & Just Intonation & Diff (cents) \\')
print(r'\midrule')
for i in range(len(intervals)):
    print(f"{intervals[i]} & {equal_temp[i]:.4f} & {just_int[i]:.4f} & {cents_diff[i]:.1f} \\\\")
print(r'\bottomrule')
print(r'\end{tabular}')
print(r'\label{tab:intervals}')
print(r'\end{table}')
\end{pycode}

\section{Conclusions}

This analysis demonstrates fundamental concepts in musical acoustics including harmonic generation, vibration modes, and tuning systems. The differences between equal temperament and just intonation become significant for intervals like the major third (14 cents) and explain why these intervals may sound "out of tune" in equal temperament.

\end{document}
'''

write_template('acoustics', 'room_acoustics.tex', room_acoustics)
write_template('acoustics', 'sound_propagation.tex', sound_propagation)
write_template('acoustics', 'musical_acoustics.tex', musical_acoustics)

print("\nAcoustics templates completed (3/100)")
