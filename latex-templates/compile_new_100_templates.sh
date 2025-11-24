#!/bin/bash
# Compile all 100 NEW computational math and science templates
# Each template is compiled with PythonTeX

set -e  # Exit on error

BASE_DIR="/home/user/latex-templates/templates"
OUTPUT_DIR="/home/user/latex-templates/output"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Counter for progress
TOTAL=100
COUNT=0

# Function to compile a PythonTeX template
compile_template() {
    local category="$1"
    local template="$2"
    local base_name="${template%.tex}"
    local template_path="$BASE_DIR/$category/$template"
    local output_name="${category}_${base_name}.pdf"

    echo "[$((COUNT + 1))/$TOTAL] Compiling: $category/$template"

    cd "$BASE_DIR/$category"

    # Pass 1: Initial LaTeX run (allow missing image errors)
    pdflatex -interaction=nonstopmode "$template" > /dev/null 2>&1

    # Pass 2: PythonTeX execution
    pythontex "$template" > /dev/null 2>&1 || {
        echo "  WARNING: pythontex failed for $category/$template"
        COUNT=$((COUNT + 1))
        return
    }

    # Pass 3: Final LaTeX run
    pdflatex -interaction=nonstopmode "$template" > /dev/null 2>&1 || {
        echo "  WARNING: Final pdflatex failed for $category/$template"
        COUNT=$((COUNT + 1))
        return
    }

    # Copy PDF to output directory with renamed format
    if [ -f "$base_name.pdf" ]; then
        cp "$base_name.pdf" "$OUTPUT_DIR/$output_name"
        echo "  SUCCESS: Created $output_name"
    else
        echo "  ERROR: PDF not generated for $category/$template"
    fi

    # Cleanup auxiliary files
    rm -f *.aux *.log *.out *.toc *.pytxcode *.fls *.fdb_latexmk
    rm -rf pythontex-files-*

    COUNT=$((COUNT + 1))
    cd - > /dev/null
}

echo "======================================"
echo "Compiling 100 New Templates"
echo "======================================"
echo ""

# Acoustics (3)
compile_template "acoustics" "room_acoustics.tex"
compile_template "acoustics" "sound_propagation.tex"
compile_template "acoustics" "musical_acoustics.tex"

# Astrophysics (4)
compile_template "astrophysics" "black_holes.tex"
compile_template "astrophysics" "gravitational_waves.tex"
compile_template "astrophysics" "neutron_stars.tex"
compile_template "astrophysics" "galaxy_dynamics.tex"

# Atmospheric Science (3)
compile_template "atmospheric-science" "atmospheric_dynamics.tex"
compile_template "atmospheric-science" "radiative_transfer.tex"
compile_template "atmospheric-science" "air_pollution.tex"

# Biomedical Engineering (4)
compile_template "biomedical" "biomechanics.tex"
compile_template "biomedical" "pharmacokinetics.tex"
compile_template "biomedical" "medical_imaging.tex"
compile_template "biomedical" "biosignal_processing.tex"

# Chemical Engineering (4)
compile_template "chemical-engineering" "reaction_engineering.tex"
compile_template "chemical-engineering" "mass_transfer.tex"
compile_template "chemical-engineering" "process_control.tex"
compile_template "chemical-engineering" "separation_processes.tex"

# Civil Engineering (3)
compile_template "civil-engineering" "structural_analysis.tex"
compile_template "civil-engineering" "soil_mechanics.tex"
compile_template "civil-engineering" "traffic_flow.tex"

# Cognitive Science (3)
compile_template "cognitive-science" "decision_making.tex"
compile_template "cognitive-science" "memory_models.tex"
compile_template "cognitive-science" "attention.tex"

# Computational Biology (4)
compile_template "computational-biology" "protein_folding.tex"
compile_template "computational-biology" "metabolic_networks.tex"
compile_template "computational-biology" "genetic_algorithms.tex"
compile_template "computational-biology" "cellular_automata.tex"

# Control Theory (3)
compile_template "control-theory" "optimal_control.tex"
compile_template "control-theory" "adaptive_control.tex"
compile_template "control-theory" "nonlinear_control.tex"

# Cosmology (3)
compile_template "cosmology" "big_bang.tex"
compile_template "cosmology" "inflation.tex"
compile_template "cosmology" "structure_formation.tex"

# Cryptography (3)
compile_template "cryptography" "rsa_encryption.tex"
compile_template "cryptography" "hash_functions.tex"
compile_template "cryptography" "elliptic_curves.tex"

# Ecology (4)
compile_template "ecology" "food_webs.tex"
compile_template "ecology" "species_distribution.tex"
compile_template "ecology" "island_biogeography.tex"
compile_template "ecology" "metapopulation.tex"

# Electromagnetics (4)
compile_template "electromagnetics" "wave_propagation.tex"
compile_template "electromagnetics" "antenna_design.tex"
compile_template "electromagnetics" "emc.tex"
compile_template "electromagnetics" "microwave.tex"

# Epidemiology (3)
compile_template "epidemiology" "seir_model.tex"
compile_template "epidemiology" "network_epidemics.tex"
compile_template "epidemiology" "spatial_epidemiology.tex"

# Financial Mathematics (4)
compile_template "financial-math" "option_pricing.tex"
compile_template "financial-math" "portfolio_optimization.tex"
compile_template "financial-math" "risk_management.tex"
compile_template "financial-math" "time_series_finance.tex"

# Game Development (3)
compile_template "game-development" "procedural_generation.tex"
compile_template "game-development" "physics_simulation.tex"
compile_template "game-development" "pathfinding.tex"

# Geochemistry (3)
compile_template "geochemistry" "isotope_geochemistry.tex"
compile_template "geochemistry" "aqueous_geochemistry.tex"
compile_template "geochemistry" "mineral_thermodynamics.tex"

# Hydrology (3)
compile_template "hydrology" "rainfall_runoff.tex"
compile_template "hydrology" "groundwater_flow.tex"
compile_template "hydrology" "flood_frequency.tex"

# Image Processing (4)
compile_template "image-processing" "edge_detection.tex"
compile_template "image-processing" "image_filtering.tex"
compile_template "image-processing" "morphological.tex"
compile_template "image-processing" "segmentation.tex"

# Marine Biology (3)
compile_template "marine-biology" "ocean_productivity.tex"
compile_template "marine-biology" "population_genetics.tex"
compile_template "marine-biology" "fisheries_models.tex"

# Operations Research (4)
compile_template "operations-research" "linear_programming.tex"
compile_template "operations-research" "queueing_theory.tex"
compile_template "operations-research" "inventory_models.tex"
compile_template "operations-research" "scheduling.tex"

# Photonics (3)
compile_template "photonics" "laser_physics.tex"
compile_template "photonics" "nonlinear_optics.tex"
compile_template "photonics" "photonic_crystals.tex"

# Plasma Physics (3)
compile_template "plasma-physics" "plasma_parameters.tex"
compile_template "plasma-physics" "mhd.tex"
compile_template "plasma-physics" "plasma_waves.tex"

# Power Systems (3)
compile_template "power-systems" "load_flow.tex"
compile_template "power-systems" "transient_stability.tex"
compile_template "power-systems" "renewable_integration.tex"

# Probability Theory (4)
compile_template "probability" "markov_chains.tex"
compile_template "probability" "random_walks.tex"
compile_template "probability" "extreme_value.tex"
compile_template "probability" "point_processes.tex"

# Psychophysics (3)
compile_template "psychophysics" "weber_fechner.tex"
compile_template "psychophysics" "signal_detection.tex"
compile_template "psychophysics" "color_perception.tex"

# Quantum Mechanics (4)
compile_template "quantum-mechanics" "harmonic_oscillator.tex"
compile_template "quantum-mechanics" "hydrogen_atom.tex"
compile_template "quantum-mechanics" "perturbation_theory.tex"
compile_template "quantum-mechanics" "scattering.tex"

# Relativity (3)
compile_template "relativity" "special_relativity.tex"
compile_template "relativity" "general_relativity.tex"
compile_template "relativity" "gravitational_lensing.tex"

# Semiconductor Physics (3)
compile_template "semiconductor" "band_theory.tex"
compile_template "semiconductor" "pn_junctions.tex"
compile_template "semiconductor" "mosfet.tex"

# Systems Biology (2)
compile_template "systems-biology" "gene_regulatory.tex"
compile_template "systems-biology" "signal_transduction.tex"

echo ""
echo "======================================"
echo "Compilation Summary"
echo "======================================"
echo "Total templates processed: $COUNT/$TOTAL"
echo "Output directory: $OUTPUT_DIR"
echo ""
echo "Listing generated PDFs:"
ls -1 "$OUTPUT_DIR" | grep -E "^(acoustics|astrophysics|atmospheric-science|biomedical|chemical-engineering|civil-engineering|cognitive-science|computational-biology|control-theory|cosmology|cryptography|ecology|electromagnetics|epidemiology|financial-math|game-development|geochemistry|hydrology|image-processing|marine-biology|operations-research|photonics|plasma-physics|power-systems|probability|psychophysics|quantum-mechanics|relativity|semiconductor|systems-biology)" | wc -l
echo "new template PDFs created"
