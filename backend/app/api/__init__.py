"""
API Routes Module
"""

from flask import Blueprint

graph_bp = Blueprint('graph', __name__)
simulation_bp = Blueprint('simulation', __name__)
report_bp = Blueprint('report', __name__)
settings_bp = Blueprint('settings', __name__)

from . import (
    graph,  # noqa: E402, F401
    report,  # noqa: E402, F401
    settings,  # noqa: E402, F401
    simulation,  # noqa: E402, F401
)

