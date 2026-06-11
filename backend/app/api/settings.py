"""
Settings API Routes
Reads and writes a curated set of configuration values stored in the
root .env file (the same file backend/app/config.py loads at startup).
"""

import os

from dotenv import set_key
from flask import jsonify, request

from ..config import Config
from ..utils.logger import get_logger
from . import settings_bp

logger = get_logger('mirofish.api.settings')

# Repo root .env, the same file config.py loads (backend/app/config.py uses '../../.env')
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.env'))

# Curated whitelist of editable keys. Anything not listed here is rejected.
SETTINGS_GROUPS = [
    {
        'id': 'llm',
        'label': 'LLM',
        'description': 'Chat model used for ontology extraction, profile generation, and the report agent.',
        'keys': [
            {'key': 'LLM_API_KEY', 'label': 'API Key', 'secret': True, 'restart_required': False},
            {'key': 'LLM_BASE_URL', 'label': 'Base URL', 'secret': False, 'restart_required': False},
            {'key': 'LLM_MODEL_NAME', 'label': 'Model Name', 'secret': False, 'restart_required': False},
        ],
    },
    {
        'id': 'embeddings',
        'label': 'Embeddings',
        'description': 'OpenAI-compatible /embeddings endpoint used for graph vector search.',
        'keys': [
            {
                'key': 'EMBEDDING_API_KEY', 'label': 'API Key', 'secret': True, 'restart_required': False,
                'description': 'Optional. Falls back to the LLM API key when empty.',
            },
            {'key': 'EMBEDDING_BASE_URL', 'label': 'Base URL', 'secret': False, 'restart_required': False},
            {'key': 'EMBEDDING_MODEL', 'label': 'Model', 'secret': False, 'restart_required': False},
            {
                'key': 'EMBEDDING_DIMENSIONS', 'label': 'Dimensions', 'secret': False, 'restart_required': True,
                'description': 'Must match the embedding model vector size. Changing it recreates the Neo4j vector indexes at startup; existing graphs must be rebuilt.',
            },
        ],
    },
    {
        'id': 'neo4j',
        'label': 'Neo4j',
        'description': 'Graph database connection. Changes take effect after a backend restart.',
        'keys': [
            {'key': 'NEO4J_URI', 'label': 'URI', 'secret': False, 'restart_required': True},
            {'key': 'NEO4J_USER', 'label': 'User', 'secret': False, 'restart_required': True},
            {'key': 'NEO4J_PASSWORD', 'label': 'Password', 'secret': True, 'restart_required': True},
        ],
    },
    {
        'id': 'notifications',
        'label': 'Notifications',
        'description': 'ntfy push notifications. Disabled unless a topic is set.',
        'keys': [
            {'key': 'NTFY_URL', 'label': 'Server URL', 'secret': False, 'restart_required': False},
            {'key': 'NTFY_TOPIC', 'label': 'Topic', 'secret': False, 'restart_required': False},
            {'key': 'NTFY_TOKEN', 'label': 'Access Token', 'secret': True, 'restart_required': False},
        ],
    },
    {
        'id': 'oasis',
        'label': 'OASIS / CAMEL',
        'description': 'Read by the simulation subprocess (CAMEL-AI does not use the LLM settings above).',
        'keys': [
            {'key': 'OPENAI_API_KEY', 'label': 'API Key', 'secret': True, 'restart_required': False},
            {'key': 'OPENAI_API_BASE_URL', 'label': 'API Base URL', 'secret': False, 'restart_required': False},
        ],
    },
]

# Flat lookup: key name -> metadata
SETTINGS_KEYS = {
    item['key']: item
    for group in SETTINGS_GROUPS
    for item in group['keys']
}


def _current_value(key: str) -> str:
    """Resolve the current effective value of a key."""
    value = os.environ.get(key)
    if value is not None:
        return value
    # EMBEDDING_API_KEY intentionally skips the Config fallback: the Config
    # attribute bakes in the LLM_API_KEY default, but the UI should show the
    # field as unset when it is not explicitly configured.
    if key != 'EMBEDDING_API_KEY' and hasattr(Config, key):
        attr = getattr(Config, key)
        if attr is not None:
            return str(attr)
    return ''


def _mask(value: str) -> str:
    """Mask a secret: empty string if unset, otherwise '****' + last 4 chars."""
    if not value:
        return ''
    return '****' + value[-4:]


@settings_bp.route('', methods=['GET'])
@settings_bp.route('/', methods=['GET'])
def get_settings():
    """Return all editable settings grouped, with secrets masked."""
    try:
        groups = []
        for group in SETTINGS_GROUPS:
            keys = []
            for item in group['keys']:
                value = _current_value(item['key'])
                entry = {
                    'key': item['key'],
                    'label': item['label'],
                    'secret': item.get('secret', False),
                    'restart_required': item.get('restart_required', False),
                    'description': item.get('description', ''),
                }
                if entry['secret']:
                    entry['value'] = _mask(value)
                    entry['set'] = bool(value)
                else:
                    entry['value'] = value
                keys.append(entry)
            groups.append({
                'id': group['id'],
                'label': group['label'],
                'description': group.get('description', ''),
                'keys': keys,
            })
        return jsonify({"success": True, "data": {"groups": groups}})
    except Exception as e:
        logger.error(f"Failed to read settings: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@settings_bp.route('', methods=['POST'])
@settings_bp.route('/', methods=['POST'])
def update_settings():
    """Write submitted settings to the root .env file and apply them at runtime."""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not data:
            return jsonify({"success": False, "error": "Request body must be a JSON object of {key: value}"}), 400

        unknown = sorted(k for k in data if k not in SETTINGS_KEYS)
        if unknown:
            return jsonify({"success": False, "error": f"Unknown settings keys: {', '.join(unknown)}"}), 400

        updates = {}
        skipped = []
        for key, raw in data.items():
            meta = SETTINGS_KEYS[key]
            value = '' if raw is None else str(raw).strip()

            # A secret submitted in its masked form means "unchanged", skip it
            if meta.get('secret') and value == _mask(_current_value(key)):
                skipped.append(key)
                continue

            if key == 'EMBEDDING_DIMENSIONS':
                try:
                    dimensions = int(value)
                    if dimensions <= 0:
                        raise ValueError
                except ValueError:
                    return jsonify({"success": False, "error": "EMBEDDING_DIMENSIONS must be a positive integer"}), 400
                value = str(dimensions)

            updates[key] = value

        # Create the .env file if it does not exist yet
        if not os.path.exists(ENV_PATH):
            open(ENV_PATH, 'a', encoding='utf-8').close()
            logger.info(f"Created .env file at {ENV_PATH}")

        applied = []
        restart_required = []
        for key, value in updates.items():
            set_key(ENV_PATH, key, value, quote_mode='auto')
            os.environ[key] = value

            # Apply at runtime where a matching Config attribute exists
            if hasattr(Config, key):
                setattr(Config, key, int(value) if key == 'EMBEDDING_DIMENSIONS' else value)
            # Keep the derived embedding key fallback in sync with LLM_API_KEY
            if key == 'LLM_API_KEY' and not os.environ.get('EMBEDDING_API_KEY'):
                Config.EMBEDDING_API_KEY = value

            applied.append(key)
            if SETTINGS_KEYS[key].get('restart_required'):
                restart_required.append(key)

        if applied:
            logger.info(f"Settings updated: {', '.join(applied)}")

        return jsonify({"success": True, "data": {
            "applied": applied,
            "skipped": skipped,
            "restart_required": restart_required,
        }})
    except Exception as e:
        logger.error(f"Failed to update settings: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
