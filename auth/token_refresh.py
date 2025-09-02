

import logging

from fastapi.security import HTTPBearer

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

