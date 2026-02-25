# FreeCAD Skill for Gemini CLI 🛠️

The first native **Gemini CLI skill** for automated 3D modeling, CAD engineering, and differentiable physical optimization. This skill transforms Gemini CLI into an autonomous CAD engineer capable of designing, simulating, and optimizing 3D structures through the FreeCAD Python API.

## 🌟 Key Features

- **Autonomous 3D Modeling:** Ask Gemini to design complex parts (brackets, flanges, gears) using natural language.
- **Differentiable CAD:** Integrated with **JAX-FEM** for automated structural optimization (e.g., finding the optimal radius for a tree trunk based on physical loads).
- **Headless CLI Workflow:** Optimized for terminal environments using `freecadcmd` and `xvfb-run`.
- **Multi-Format Export:** Seamlessly export to **STEP** (CAD), **STL** (3D Printing), and **GLB** (Web/AR) with automatic Y-up orientation.
- **Direct Python Control:** Allows the agent to write and execute high-fidelity Python scripts for precise geometric control.

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have the following installed on your system:
- **FreeCAD Desktop** (provides the Python libraries)
- **xvfb** (for headless execution)
- **obj2gltf** (for GLB conversion)

```bash
# Linux (Debian/Ubuntu)
sudo apt update && sudo apt install freecad xvfb -y
npm install -g obj2gltf
```

### 2. Installation
Install the skill directly into your Gemini CLI environment:

```bash
# Clone the repository
git clone https://github.com/1kaiser/freecad-skill.git
cd freecad-skill

# Install via Gemini CLI
gemini skills install ./freecad --scope user
```

### 3. Usage
Once installed, reload your skills (`/skills reload`) and command the agent:

```text
"Design a 3D tree with a 50mm trunk and export it as a GLB."
"Optimize the thickness of a support bracket to handle a 100N load using JAX-FEM."
"Create a STEP file for a custom cooling manifold with integrated fins."
```

## 📁 Repository Structure

```text
.
├── freecad/            # Native Gemini CLI Skill Definition (SKILL.md)
├── examples/           # Procedural and Differentiable CAD examples
│   ├── create_tree.py  # Basic procedural modeling
│   ├── optimize_tree.py# JAX-FEM structural optimization
│   └── colored_tree.py # High-fidelity GLB with vertex colors
└── README.md           # Professional documentation
```

## 🧪 Advanced: Differentiable Optimization
This skill is unique in its support for **JAX-based physics-driven design**. By combining FreeCAD's geometry engine with JAX-FEM, the agent can:
1. Initialize a base geometry in FreeCAD.
2. Differentiate through a FEM simulation to find optimal parameters.
3. Update the high-fidelity CAD model with the optimized results.

## 📚 References & Acknowledgments

### Foundational Frameworks
- **[Gemini CLI](https://github.com/google/gemini-cli):** The primary agent interface and skill system provider.
- **[FreeCAD](https://www.freecad.org/):** The open-source parametric 3D modeler powering the geometric engine.
- **[JAX-FEM](https://github.com/deepmodeling/jax-fem):** The differentiable finite element package enabling structural optimization.

### Inspiration & Community
- **[drawio-mcp](https://github.com/1kaiser/drawio-mcp):** Inspired the "Skill + CLI" architectural pattern for seamless tool integration.
- **[freecad-mcp](https://github.com/neka-nat/freecad-mcp):** Provided initial insights into MCP-based CAD control.

### Academic Citations
If you use this workflow in academic research, please consider citing the following foundational works:

**JAX-FEM (Structural Optimization):**
```bibtex
@article{xue2023jax,
  title={JAX-FEM: A differentiable GPU-accelerated 3D finite element solver for automatic inverse design and mechanistic data science},
  author={Xue, Tianju and Liao, Shuheng and Gan, Zhengtao and Park, Chanwook and Xie, Xiaoyu and Liu, Wing Kam and Cao, Jian},
  journal={Computer Physics Communications},
  pages={108802},
  year={2023},
  publisher={Elsevier}
}
```

**FreeCAD (Geometric Modeling):**
```bibtex
@online{freecad2024,
  author = {The FreeCAD Team},
  title = {FreeCAD: An open-source parametric 3D modeler},
  year = {2024},
  url = {https://www.freecad.org}
}
```

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
Created and maintained by [1kaiser](https://github.com/1kaiser)
