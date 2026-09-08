"""3D Bloch sphere mathematical representation and Plotly visualization figures."""

from __future__ import annotations
import math
from typing import Tuple, Optional, List, Dict, Any
import numpy as np
import plotly.graph_objects as go

from quantum_lab.states import QuantumState


class BlochSphereVisualizer:
    """Generates 3D interactive Plotly figures for Bloch sphere state analysis."""

    @classmethod
    def create_bloch_figure(
        cls,
        expected_state: Optional[QuantumState] = None,
        reconstructed_state: Optional[QuantumState] = None,
        attack_state: Optional[QuantumState] = None,
        title: str = "3D Quantum Bloch Sphere Telemetry",
    ) -> go.Figure:
        """Constructs a 3D Bloch sphere with state vectors and basis markers."""
        fig = go.Figure()

        # 1. Wireframe Sphere
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        xs = np.outer(np.cos(u), np.sin(v))
        ys = np.outer(np.sin(u), np.sin(v))
        zs = np.outer(np.ones(np.size(u)), np.cos(v))

        fig.add_trace(
            go.Surface(
                x=xs,
                y=ys,
                z=zs,
                opacity=0.15,
                colorscale=[[0, "#00f2fe"], [1, "#4facfe"]],
                showscale=False,
                hoverinfo="none",
            )
        )

        # 2. Axes Lines
        axis_len = 1.25
        # Z-axis
        fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[-axis_len, axis_len], mode="lines", line=dict(color="#888888", width=2), showlegend=False))
        # X-axis
        fig.add_trace(go.Scatter3d(x=[-axis_len, axis_len], y=[0, 0], z=[0, 0], mode="lines", line=dict(color="#888888", width=2), showlegend=False))
        # Y-axis
        fig.add_trace(go.Scatter3d(x=[0, 0], y=[-axis_len, axis_len], z=[0, 0], mode="lines", line=dict(color="#888888", width=2), showlegend=False))

        # 3. Basis Pole Labels
        poles_x = [0, 0, 1.15, -1.15, 0, 0]
        poles_y = [0, 0, 0, 0, 1.15, -1.15]
        poles_z = [1.15, -1.15, 0, 0, 0, 0]
        poles_text = ["|0⟩ (Z+)", "|1⟩ (Z-)", "|+⟩ (X+)", "|-⟩ (X-)", "|+i⟩ (Y+)", "|-i⟩ (Y-)"]

        fig.add_trace(
            go.Scatter3d(
                x=poles_x,
                y=poles_y,
                z=poles_z,
                mode="text",
                text=poles_text,
                textfont=dict(color="#00ffff", size=11),
                showlegend=False,
            )
        )

        # 4. Expected State Vector (Green)
        if expected_state:
            rx, ry, rz = expected_state.bloch_coordinates
            fig.add_trace(
                go.Scatter3d(
                    x=[0, rx],
                    y=[0, ry],
                    z=[0, rz],
                    mode="lines+markers",
                    line=dict(color="#00ff88", width=6),
                    marker=dict(size=[0, 7], color="#00ff88"),
                    name=f"Expected State ({expected_state.family.value})",
                )
            )

        # 5. Reconstructed State Vector (Cyan)
        if reconstructed_state:
            rx, ry, rz = reconstructed_state.bloch_coordinates
            fig.add_trace(
                go.Scatter3d(
                    x=[0, rx],
                    y=[0, ry],
                    z=[0, rz],
                    mode="lines+markers",
                    line=dict(color="#00d4ff", width=5, dash="dash"),
                    marker=dict(size=[0, 6], color="#00d4ff"),
                    name="Reconstructed (Bob)",
                )
            )

        # 6. Post-Attack State Vector (Red/Pink)
        if attack_state:
            rx, ry, rz = attack_state.bloch_coordinates
            fig.add_trace(
                go.Scatter3d(
                    x=[0, rx],
                    y=[0, ry],
                    z=[0, rz],
                    mode="lines+markers",
                    line=dict(color="#ff0055", width=5),
                    marker=dict(size=[0, 7], color="#ff0055"),
                    name="Attacked State (Transit)",
                )
            )

        fig.update_layout(
            title=dict(text=title, font=dict(color="#ffffff", size=15)),
            paper_bgcolor="rgba(10, 15, 30, 0.95)",
            plot_bgcolor="rgba(10, 15, 30, 0.95)",
            scene=dict(
                xaxis=dict(showbackground=False, showgrid=False, zeroline=False, title="X (Hadamard)", color="#aaaaaa"),
                yaxis=dict(showbackground=False, showgrid=False, zeroline=False, title="Y (Circular)", color="#aaaaaa"),
                zaxis=dict(showbackground=False, showgrid=False, zeroline=False, title="Z (Computational)", color="#aaaaaa"),
                aspectmode="cube",
            ),
            legend=dict(font=dict(color="#ffffff"), bgcolor="rgba(20,30,50,0.8)"),
            margin=dict(l=0, r=0, b=0, t=35),
        )

        return fig
