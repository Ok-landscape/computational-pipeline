#!/usr/bin/env python3
"""
Template Enhancement Script
Generates comprehensive PythonTeX templates for all categories.
Each template includes: multiple analyses, 4-6 plots, mathematical framework,
algorithm boxes, tables, and detailed discussion.
"""

import os
import subprocess

# Base directory
BASE_DIR = "/home/user/latex-templates/templates"
OUTPUT_DIR = "/home/user/latex-templates/output"

# Template definitions with full content
TEMPLATES = {
    # AEROSPACE - remaining 2
    "aerospace/rocket_propulsion.tex": {
        "style": "lab_report",
        "title": "Rocket Propulsion Analysis: Thrust Curves, Specific Impulse, and Staging Optimization",
        "content": r'''
\begin{abstract}
This laboratory report presents a comprehensive analysis of rocket propulsion systems. We examine thrust curves for different propellant combinations, compare specific impulse values, and optimize multi-stage rocket configurations using the Tsiolkovsky equation. The analysis includes propellant mass flow rates, chamber pressure effects, and payload fraction optimization for orbital insertion.
\end{abstract}

\section{Objectives}
\begin{enumerate}
    \item Analyze thrust and specific impulse for various propellant combinations
    \item Compare single-stage and multi-stage rocket performance
    \item Optimize staging ratios for maximum payload fraction
    \item Evaluate thrust-to-weight ratios for different mission profiles
\end{enumerate}

\section{Theoretical Background}

\begin{definition}[Specific Impulse]
Specific impulse is the total impulse per unit weight of propellant:
\begin{equation}
I_{sp} = \frac{F}{\dot{m} g_0} = \frac{v_e}{g_0}
\end{equation}
where $F$ is thrust, $\dot{m}$ is mass flow rate, and $v_e$ is effective exhaust velocity.
\end{definition}

\subsection{Tsiolkovsky Rocket Equation}
The ideal velocity change achievable by a rocket:
\begin{equation}
\Delta v = v_e \ln\left(\frac{m_0}{m_f}\right) = I_{sp} g_0 \ln(MR)
\end{equation}
where $MR = m_0/m_f$ is the mass ratio.

\subsection{Staging Analysis}
For an $n$-stage rocket with equal $\Delta v$ per stage:
\begin{equation}
\Delta v_{total} = n \cdot v_e \ln(MR_{stage})
\end{equation}

The payload ratio improves significantly with staging:
\begin{equation}
\lambda = \frac{m_{payload}}{m_0} = \prod_{i=1}^{n} \frac{1}{MR_i} - \sum_{i=1}^{n} \epsilon_i
\end{equation}
where $\epsilon_i$ is the structural coefficient of stage $i$.

\section{Experimental Setup}

\begin{pycode}
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

np.random.seed(42)

g0 = 9.81  # m/s^2

# Propellant data
propellants = {
    'Solid (HTPB)': {'Isp': 265, 'density': 1800, 'cost': 10},
    'RP-1/LOX': {'Isp': 353, 'density': 1030, 'cost': 50},
    'LH2/LOX': {'Isp': 455, 'density': 360, 'cost': 200},
    'MMH/N2O4': {'Isp': 340, 'density': 1200, 'cost': 150},
    'Methalox': {'Isp': 380, 'density': 830, 'cost': 30}
}

# Mission delta-v requirements (m/s)
missions = {
    'LEO': 9400,
    'GTO': 13500,
    'Lunar': 15500,
    'Mars': 18000
}

# Function to compute payload fraction for single stage
def single_stage_payload(dv, Isp, struct_coeff=0.1):
    ve = Isp * g0
    MR = np.exp(dv / ve)
    # m_f = m_struct + m_payload = struct_coeff * m_prop + m_payload
    # MR = m_0 / m_f
    # Solving: payload_frac = 1/MR - struct_coeff * (1 - 1/MR)
    payload_frac = 1/MR - struct_coeff * (1 - 1/MR)
    return max(0, payload_frac)

# Function for n-stage rocket
def multi_stage_payload(dv, Isp, n_stages, struct_coeff=0.1):
    ve = Isp * g0
    dv_per_stage = dv / n_stages
    MR_stage = np.exp(dv_per_stage / ve)

    # Payload fraction for n stages
    payload_frac = 1.0
    for _ in range(n_stages):
        stage_payload = 1/MR_stage - struct_coeff * (1 - 1/MR_stage)
        if stage_payload <= 0:
            return 0
        payload_frac *= stage_payload
    return payload_frac

# Thrust curve simulation
def thrust_curve(t, F_max, t_burn, profile='constant'):
    if profile == 'constant':
        return np.where(t <= t_burn, F_max, 0)
    elif profile == 'regressive':
        return np.where(t <= t_burn, F_max * (1 - 0.3 * t/t_burn), 0)
    elif profile == 'progressive':
        return np.where(t <= t_burn, F_max * (0.7 + 0.3 * t/t_burn), 0)

# Time array
t = np.linspace(0, 150, 1000)

# Simulate thrust curves
F_max = 1e6  # N
t_burn = 120  # s
profiles = ['constant', 'regressive', 'progressive']
thrust_curves = {p: thrust_curve(t, F_max, t_burn, p) for p in profiles}

# Staging optimization
n_stages_range = range(1, 6)
staging_results = {}
for mission, dv in missions.items():
    staging_results[mission] = []
    for n in n_stages_range:
        # Use best propellant (LH2/LOX)
        pf = multi_stage_payload(dv, 455, n, 0.08)
        staging_results[mission].append(pf * 100)  # Convert to percentage

# Create comprehensive visualization
fig = plt.figure(figsize=(14, 12))

# Plot 1: Thrust curves
ax1 = fig.add_subplot(2, 3, 1)
colors = ['blue', 'red', 'green']
for prof, color in zip(profiles, colors):
    ax1.plot(t, thrust_curves[prof]/1e6, color=color, linewidth=2,
             label=prof.capitalize())
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Thrust (MN)')
ax1.set_title('Thrust Curve Profiles')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# Plot 2: Specific impulse comparison
ax2 = fig.add_subplot(2, 3, 2)
names = list(propellants.keys())
isps = [propellants[n]['Isp'] for n in names]
densities = [propellants[n]['density'] for n in names]
x = np.arange(len(names))
width = 0.35
bars1 = ax2.bar(x - width/2, isps, width, label='$I_{sp}$ (s)', color='steelblue')
ax2_twin = ax2.twinx()
bars2 = ax2_twin.bar(x + width/2, densities, width, label='Density (kg/m$^3$)', color='coral')
ax2.set_xlabel('Propellant')
ax2.set_ylabel('$I_{sp}$ (s)', color='steelblue')
ax2_twin.set_ylabel('Density (kg/m$^3$)', color='coral')
ax2.set_xticks(x)
ax2.set_xticklabels([n.split()[0] for n in names], rotation=45, ha='right')
ax2.set_title('Propellant Comparison')
ax2.legend(loc='upper left', fontsize=7)
ax2_twin.legend(loc='upper right', fontsize=7)

# Plot 3: Single-stage payload fraction
ax3 = fig.add_subplot(2, 3, 3)
dv_range = np.linspace(1000, 12000, 100)
for name in ['RP-1/LOX', 'LH2/LOX', 'Methalox']:
    pf = [single_stage_payload(dv, propellants[name]['Isp']) * 100 for dv in dv_range]
    ax3.plot(dv_range/1000, pf, linewidth=2, label=name)
ax3.axvline(x=9.4, color='gray', linestyle='--', alpha=0.7)
ax3.text(9.5, 15, 'LEO', fontsize=8)
ax3.set_xlabel(r'$\Delta v$ (km/s)')
ax3.set_ylabel('Payload Fraction (\%)')
ax3.set_title('Single-Stage Performance')
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)
ax3.set_ylim([0, 30])

# Plot 4: Staging benefits
ax4 = fig.add_subplot(2, 3, 4)
for mission in ['LEO', 'GTO', 'Mars']:
    ax4.plot(list(n_stages_range), staging_results[mission], 'o-',
             linewidth=2, markersize=6, label=mission)
ax4.set_xlabel('Number of Stages')
ax4.set_ylabel('Payload Fraction (\%)')
ax4.set_title('Staging Optimization (LH2/LOX)')
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3)
ax4.set_xticks(list(n_stages_range))

# Plot 5: Delta-v requirements
ax5 = fig.add_subplot(2, 3, 5)
mission_names = list(missions.keys())
dvs = [missions[m]/1000 for m in mission_names]
colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(missions)))
bars = ax5.bar(mission_names, dvs, color=colors)
ax5.set_xlabel('Mission')
ax5.set_ylabel(r'$\Delta v$ (km/s)')
ax5.set_title('Mission Delta-v Requirements')
for bar, dv in zip(bars, dvs):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
             f'{dv:.1f}', ha='center', va='bottom', fontsize=9)
ax5.grid(True, alpha=0.3, axis='y')

# Plot 6: Mass ratio requirements
ax6 = fig.add_subplot(2, 3, 6)
Isp_range = np.linspace(250, 500, 100)
for mission in ['LEO', 'GTO']:
    MR = np.exp(missions[mission] / (Isp_range * g0))
    ax6.plot(Isp_range, MR, linewidth=2, label=mission)
ax6.set_xlabel('$I_{sp}$ (s)')
ax6.set_ylabel('Required Mass Ratio')
ax6.set_title('Mass Ratio vs Specific Impulse')
ax6.legend(fontsize=8)
ax6.grid(True, alpha=0.3)
ax6.set_ylim([0, 50])

plt.tight_layout()
plt.savefig('rocket_propulsion_plot.pdf', bbox_inches='tight', dpi=150)
print(r'\begin{center}')
print(r'\includegraphics[width=\textwidth]{rocket_propulsion_plot.pdf}')
print(r'\end{center}')
plt.close()

# Key results
best_2stage = staging_results['LEO'][1]
best_3stage = staging_results['LEO'][2]
\end{pycode}

\section{Algorithm}

\begin{algorithm}[H]
\SetAlgoLined
\KwIn{Mission $\Delta v$, propellant $I_{sp}$, number of stages $n$, structural coefficient $\epsilon$}
\KwOut{Payload fraction $\lambda$}
$v_e \leftarrow I_{sp} \cdot g_0$\;
$\Delta v_{stage} \leftarrow \Delta v / n$\;
$MR_{stage} \leftarrow \exp(\Delta v_{stage} / v_e)$\;
$\lambda \leftarrow 1$\;
\For{$i = 1$ \KwTo $n$}{
    $\lambda_{stage} \leftarrow 1/MR_{stage} - \epsilon(1 - 1/MR_{stage})$\;
    $\lambda \leftarrow \lambda \cdot \lambda_{stage}$\;
}
\Return{$\lambda$}
\caption{Multi-Stage Payload Fraction}
\end{algorithm}

\section{Results and Observations}

\subsection{Propellant Performance}

\begin{pycode}
print(r'\begin{table}[h]')
print(r'\centering')
print(r'\caption{Propellant Performance Comparison}')
print(r'\begin{tabular}{lccc}')
print(r'\toprule')
print(r'Propellant & $I_{sp}$ (s) & Density (kg/m$^3$) & Density $I_{sp}$ \\')
print(r'\midrule')
for name, data in propellants.items():
    density_isp = data['Isp'] * data['density'] / 1000
    print(f"{name} & {data['Isp']} & {data['density']} & {density_isp:.0f} \\\\")
print(r'\bottomrule')
print(r'\end{tabular}')
print(r'\end{table}')
\end{pycode}

\subsection{Staging Benefits}
For LEO insertion ($\Delta v = 9.4$ km/s) with LH2/LOX:
\begin{itemize}
    \item Single stage: \py{f"{staging_results['LEO'][0]:.1f}"}\% payload fraction
    \item Two stages: \py{f"{best_2stage:.1f}"}\% payload fraction
    \item Three stages: \py{f"{best_3stage:.1f}"}\% payload fraction
\end{itemize}

\begin{remark}[Diminishing Returns]
Adding stages beyond 3 provides marginal improvement while significantly increasing complexity and cost. Most modern launch vehicles use 2-3 stages as an optimal trade-off.
\end{remark}

\section{Conclusions}
\begin{itemize}
    \item LH2/LOX provides highest $I_{sp}$ (455 s) but lowest density
    \item RP-1/LOX offers good balance of performance and handling
    \item Staging dramatically improves payload fraction for high $\Delta v$ missions
    \item Optimal stage count is 2-3 for most Earth-to-orbit missions
\end{itemize}

\section*{References}
\begin{itemize}
    \item Sutton, G. P., \& Biblarz, O. (2016). \textit{Rocket Propulsion Elements}. Wiley.
    \item Turner, M. J. L. (2008). \textit{Rocket and Spacecraft Propulsion}. Springer.
\end{itemize}
'''
    },

    "aerospace/satellite_coverage.tex": {
        "style": "technical_report",
        "title": "Satellite Coverage Analysis: Ground Coverage, Revisit Times, and Constellation Design",
        "content": r'''
\begin{abstract}
This technical report presents a comprehensive analysis of satellite ground coverage for Earth observation and communication missions. We compute instantaneous coverage footprints, revisit times for single satellites and constellations, and optimize Walker constellation parameters for global coverage. The analysis includes elevation angle constraints, atmospheric effects, and coverage gap analysis for critical applications.
\end{abstract}

\section{Executive Summary}
Satellite coverage analysis is critical for mission design in Earth observation, communications, and navigation applications. This report analyzes coverage characteristics for various orbital configurations and provides design guidelines for constellation optimization.

\section{Mathematical Framework}

\begin{definition}[Coverage Half-Angle]
The Earth-central angle from the sub-satellite point to the coverage edge:
\begin{equation}
\rho = \arccos\left(\frac{R_E}{R_E + h}\cos\varepsilon_{min}\right) - \varepsilon_{min}
\end{equation}
where $\varepsilon_{min}$ is the minimum elevation angle and $h$ is orbital altitude.
\end{definition}

\subsection{Coverage Area}
The instantaneous coverage area on Earth's surface:
\begin{equation}
A_{cov} = 2\pi R_E^2 (1 - \cos\rho)
\end{equation}

\subsection{Revisit Time}
For a single satellite in a circular orbit:
\begin{equation}
T_{revisit} \approx \frac{2\pi R_E \cos\phi}{v_{ground}} \cdot \frac{1}{N_{orbits/day}}
\end{equation}
where $\phi$ is latitude and $v_{ground}$ is the ground track velocity.

\subsection{Walker Constellation}
A Walker Delta pattern is described by $T/P/F$:
\begin{itemize}
    \item $T$ = Total number of satellites
    \item $P$ = Number of orbital planes
    \item $F$ = Relative phasing between planes
\end{itemize}

\section{Computational Analysis}

\begin{pycode}
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

np.random.seed(42)

# Constants
R_earth = 6371  # km
mu = 398600  # km^3/s^2
omega_E = 7.2921e-5  # rad/s

# Function to compute coverage parameters
def coverage_params(h, elev_min_deg):
    elev_min = np.deg2rad(elev_min_deg)
    # Earth central angle
    sin_rho = (R_earth + h) / R_earth * np.cos(elev_min) - np.sin(elev_min) / np.tan(elev_min + np.arcsin((R_earth/(R_earth+h))*np.cos(elev_min)))
    rho = np.arccos(R_earth / (R_earth + h) * np.cos(elev_min)) - elev_min

    # Coverage area
    area = 2 * np.pi * R_earth**2 * (1 - np.cos(rho))

    # Swath width
    swath = 2 * R_earth * np.sin(rho)

    # Slant range
    slant_range = R_earth * (np.sin(rho) / np.sin(elev_min + rho))

    return np.rad2deg(rho), area, swath, slant_range

# Orbital configurations to analyze
altitudes = [400, 600, 800, 1200, 2000]  # km
elev_angles = [5, 10, 15, 20, 30]  # degrees

# Coverage vs altitude analysis
coverage_data = {}
for h in altitudes:
    rho, area, swath, slant = coverage_params(h, 10)  # 10 deg elevation
    T = 2 * np.pi * np.sqrt((R_earth + h)**3 / mu)
    coverage_data[h] = {
        'rho': rho, 'area': area, 'swath': swath,
        'slant': slant, 'period': T/60
    }

# Walker constellation analysis
def walker_coverage(T_sats, P_planes, h, elev_min):
    """Estimate coverage for Walker constellation."""
    rho, area, _, _ = coverage_params(h, elev_min)

    # Simplified coverage estimation
    single_sat_coverage = area / (4 * np.pi * R_earth**2)

    # With T satellites (accounting for overlap)
    # Using approximate formula for global coverage
    overlap_factor = 1 - (1 - single_sat_coverage)**T_sats

    return overlap_factor * 100

# Constellation configurations
constellations = {
    'Starlink': {'T': 1584, 'P': 72, 'h': 550},
    'OneWeb': {'T': 648, 'P': 18, 'h': 1200},
    'GPS': {'T': 24, 'P': 6, 'h': 20200},
    'Iridium': {'T': 66, 'P': 6, 'h': 780}
}

# Ground track simulation for single satellite
def simulate_ground_track(h, inc_deg, duration_orbits=3, n_points=1000):
    a = R_earth + h
    T = 2 * np.pi * np.sqrt(a**3 / mu)
    t = np.linspace(0, duration_orbits * T, n_points)

    n = np.sqrt(mu / a**3)
    inc = np.deg2rad(inc_deg)

    # Simplified ground track
    lat = np.rad2deg(np.arcsin(np.sin(inc) * np.sin(n * t)))
    lon = np.rad2deg(np.mod(omega_E * t - n * t + np.pi, 2*np.pi) - np.pi)

    return lat, lon, T

# Revisit time calculation
def revisit_time(h, lat_deg, swath_km):
    T = 2 * np.pi * np.sqrt((R_earth + h)**3 / mu)
    lat = np.deg2rad(lat_deg)

    # Ground track spacing per orbit
    track_spacing = 2 * np.pi * R_earth * np.cos(lat) / (86400 / T)

    # Number of orbits to cover
    n_orbits = track_spacing / swath_km

    return n_orbits * T / 3600  # hours

# Create visualization
fig = plt.figure(figsize=(14, 12))

# Plot 1: Coverage vs altitude
ax1 = fig.add_subplot(2, 3, 1)
alts = list(coverage_data.keys())
swaths = [coverage_data[h]['swath'] for h in alts]
areas = [coverage_data[h]['area']/1e6 for h in alts]  # in million km^2

ax1.plot(alts, swaths, 'bo-', linewidth=2, markersize=6, label='Swath (km)')
ax1_twin = ax1.twinx()
ax1_twin.plot(alts, areas, 'rs-', linewidth=2, markersize=6, label='Area (M km$^2$)')
ax1.set_xlabel('Altitude (km)')
ax1.set_ylabel('Swath Width (km)', color='blue')
ax1_twin.set_ylabel('Coverage Area (M km$^2$)', color='red')
ax1.set_title('Coverage vs Altitude (10$^\\circ$ elev)')
ax1.legend(loc='upper left', fontsize=8)
ax1_twin.legend(loc='lower right', fontsize=8)
ax1.grid(True, alpha=0.3)

# Plot 2: Elevation angle effects
ax2 = fig.add_subplot(2, 3, 2)
h_ref = 800
for elev in elev_angles:
    rho, area, swath, slant = coverage_params(h_ref, elev)
    ax2.bar(f'{elev}', swath, alpha=0.7)
ax2.set_xlabel('Minimum Elevation Angle (deg)')
ax2.set_ylabel('Swath Width (km)')
ax2.set_title(f'Elevation Angle Effect (h={h_ref} km)')
ax2.grid(True, alpha=0.3, axis='y')

# Plot 3: Ground track
ax3 = fig.add_subplot(2, 3, 3)
lat, lon, T = simulate_ground_track(700, 98.2, duration_orbits=2)
# Split at discontinuities
split_idx = np.where(np.abs(np.diff(lon)) > 180)[0] + 1
segments = np.split(np.arange(len(lon)), split_idx)
for seg in segments:
    if len(seg) > 1:
        ax3.plot(lon[seg], lat[seg], 'b-', linewidth=1.5, alpha=0.7)
ax3.set_xlim(-180, 180)
ax3.set_ylim(-90, 90)
ax3.set_xlabel('Longitude (deg)')
ax3.set_ylabel('Latitude (deg)')
ax3.set_title('Sun-Sync Ground Track (2 orbits)')
ax3.grid(True, alpha=0.3)

# Plot 4: Constellation comparison
ax4 = fig.add_subplot(2, 3, 4)
const_names = list(constellations.keys())
n_sats = [constellations[c]['T'] for c in const_names]
heights = [constellations[c]['h'] for c in const_names]

x = np.arange(len(const_names))
width = 0.35
bars1 = ax4.bar(x - width/2, n_sats, width, label='Satellites', color='steelblue')
ax4_twin = ax4.twinx()
bars2 = ax4_twin.bar(x + width/2, heights, width, label='Altitude (km)', color='coral')
ax4.set_xlabel('Constellation')
ax4.set_ylabel('Number of Satellites', color='steelblue')
ax4_twin.set_ylabel('Altitude (km)', color='coral')
ax4.set_xticks(x)
ax4.set_xticklabels(const_names)
ax4.set_title('Major Constellations')
ax4.legend(loc='upper left', fontsize=7)
ax4_twin.legend(loc='upper right', fontsize=7)

# Plot 5: Revisit time vs latitude
ax5 = fig.add_subplot(2, 3, 5)
lats = np.linspace(0, 80, 50)
for h in [400, 800, 1200]:
    swath = coverage_data[h]['swath'] if h in coverage_data else 2000
    revisits = [revisit_time(h, lat, swath) for lat in lats]
    ax5.plot(lats, revisits, linewidth=2, label=f'{h} km')
ax5.set_xlabel('Latitude (deg)')
ax5.set_ylabel('Revisit Time (hours)')
ax5.set_title('Single Satellite Revisit Time')
ax5.legend(fontsize=8)
ax5.grid(True, alpha=0.3)
ax5.set_ylim([0, 100])

# Plot 6: Coverage footprint
ax6 = fig.add_subplot(2, 3, 6)
theta = np.linspace(0, 2*np.pi, 100)
for h in [400, 800, 1200]:
    rho = np.deg2rad(coverage_data[h]['rho'])
    # Circular footprint approximation
    footprint_x = np.rad2deg(rho) * np.cos(theta)
    footprint_y = np.rad2deg(rho) * np.sin(theta)
    ax6.plot(footprint_x, footprint_y, linewidth=2, label=f'{h} km')
ax6.plot(0, 0, 'ko', markersize=8)
ax6.set_xlabel('Degrees from nadir')
ax6.set_ylabel('Degrees from nadir')
ax6.set_title('Coverage Footprint Comparison')
ax6.legend(fontsize=8)
ax6.grid(True, alpha=0.3)
ax6.set_aspect('equal')

plt.tight_layout()
plt.savefig('satellite_coverage_plot.pdf', bbox_inches='tight', dpi=150)
print(r'\begin{center}')
print(r'\includegraphics[width=\textwidth]{satellite_coverage_plot.pdf}')
print(r'\end{center}')
plt.close()

# Key results
h_800 = coverage_data[800]
\end{pycode}

\section{Results and Discussion}

\subsection{Altitude Trade-offs}

\begin{pycode}
print(r'\begin{table}[h]')
print(r'\centering')
print(r'\caption{Coverage Parameters vs Altitude (10$^\\circ$ min elevation)}')
print(r'\begin{tabular}{ccccc}')
print(r'\toprule')
print(r'Altitude & Period & Swath & Coverage Area & Slant Range \\')
print(r'(km) & (min) & (km) & (10$^6$ km$^2$) & (km) \\')
print(r'\midrule')
for h in altitudes:
    d = coverage_data[h]
    print(f"{h} & {d['period']:.1f} & {d['swath']:.0f} & {d['area']/1e6:.2f} & {d['slant']:.0f} \\\\")
print(r'\bottomrule')
print(r'\end{tabular}')
print(r'\end{table}')
\end{pycode}

For an 800 km altitude orbit:
\begin{itemize}
    \item Coverage half-angle: \py{f"{h_800['rho']:.1f}"}$^\circ$
    \item Swath width: \py{f"{h_800['swath']:.0f}"} km
    \item Instantaneous coverage: \py{f"{h_800['area']/1e6:.2f}"} million km$^2$
    \item Orbital period: \py{f"{h_800['period']:.1f}"} minutes
\end{itemize}

\begin{remark}[Altitude Selection]
Higher altitudes provide larger coverage footprints but at the cost of reduced resolution and increased signal latency. LEO constellations like Starlink use lower altitudes (550 km) for low latency, while GPS uses MEO (20,200 km) for fewer satellites to achieve global coverage.
\end{remark}

\section{Constellation Design Guidelines}

\subsection{Walker Delta Patterns}
\begin{itemize}
    \item \textbf{GPS (24/6/0)}: 24 satellites in 6 planes for continuous global coverage
    \item \textbf{Iridium (66/6/2)}: 66 satellites for voice/data with polar coverage
    \item \textbf{Starlink}: Massive LEO constellation for high-bandwidth internet
\end{itemize}

\section{Limitations and Extensions}
\begin{enumerate}
    \item \textbf{Spherical Earth}: Does not account for Earth oblateness
    \item \textbf{No terrain}: Ignores terrain masking effects
    \item \textbf{Simplified overlap}: Overlap estimation is approximate
\end{enumerate}

\section{Conclusion}
This analysis demonstrates the key trade-offs in satellite coverage design. Higher altitudes increase coverage but reduce resolution. Constellation design must balance satellite count against coverage requirements, with modern LEO constellations using hundreds of satellites for continuous global coverage.

\section*{References}
\begin{itemize}
    \item Wertz, J. R., \& Larson, W. J. (1999). \textit{Space Mission Analysis and Design}. Microcosm Press.
    \item Walker, J. G. (1984). Satellite constellations. Journal of the British Interplanetary Society.
\end{itemize}
'''
    },
}

# Template header
def get_preamble(style, title):
    theorem_envs = {
        "technical_report": r'''
\newtheorem{definition}{Definition}
\newtheorem{theorem}{Theorem}
\newtheorem{remark}{Remark}
''',
        "lab_report": r'''
\newtheorem{definition}{Definition}
\newtheorem{theorem}{Theorem}
\newtheorem{remark}{Remark}
''',
        "tutorial": r'''
\newtheorem{definition}{Definition}
\newtheorem{example}{Example}
\newtheorem{remark}{Remark}
''',
        "research": r'''
\newtheorem{theorem}{Theorem}
\newtheorem{lemma}{Lemma}
\newtheorem{corollary}{Corollary}
\newtheorem{proposition}{Proposition}
''',
        "textbook": r'''
\newtheorem{definition}{Definition}
\newtheorem{theorem}{Theorem}
\newtheorem{example}{Example}
\newtheorem{exercise}{Exercise}
'''
    }

    env = theorem_envs.get(style, theorem_envs["technical_report"])

    return rf'''\documentclass[a4paper, 11pt]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{amsmath, amssymb}}
\usepackage{{graphicx}}
\usepackage{{siunitx}}
\usepackage{{booktabs}}
\usepackage{{algorithm2e}}
\usepackage{{subcaption}}
\usepackage[makestderr]{{pythontex}}

{env}

\title{{{title}}}
\author{{Computational Science Templates}}
\date{{\today}}

\begin{{document}}
\maketitle
'''

def generate_template(filepath, template_data):
    """Generate a complete template file."""
    full_path = os.path.join(BASE_DIR, filepath.replace("aerospace/", "").replace("/", "/"))

    # Reconstruct the correct path
    parts = filepath.split("/")
    if len(parts) == 2:
        category, filename = parts
        full_path = os.path.join(BASE_DIR, category, filename)
    else:
        full_path = os.path.join(BASE_DIR, filepath)

    preamble = get_preamble(template_data["style"], template_data["title"])
    content = template_data["content"]

    full_content = preamble + content + "\n\\end{document}\n"

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, 'w') as f:
        f.write(full_content)

    print(f"Generated: {full_path}")

def main():
    print("Generating enhanced templates...")

    for filepath, data in TEMPLATES.items():
        generate_template(filepath, data)

    print(f"\nGenerated {len(TEMPLATES)} templates")
    print("Run compile_all.sh to build PDFs")

if __name__ == "__main__":
    main()
