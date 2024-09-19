import spectran
import sys
import logging

def main():
    log_level = sys.argv[1] if len(sys.argv) > 1 else "INFO"
    log_level = getattr(logging, log_level)
    spectran.run(level=log_level)

if __name__ == "__main__":
    main()