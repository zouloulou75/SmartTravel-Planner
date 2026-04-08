from __future__ import annotations

import json

from app.db.session import SessionLocal
from app.services.bootstrap_service import BootstrapService


def main() -> None:
    with SessionLocal() as db:
        output = BootstrapService(db).run()
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
