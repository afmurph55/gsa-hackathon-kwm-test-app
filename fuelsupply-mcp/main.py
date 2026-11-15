# Repository entry point used by stdio clients and the protocol evaluation harness.
# Server setup lives in fuelsupply.app so the installed command uses the same code.
from fuelsupply.app import main

if __name__ == "__main__":
    main()
