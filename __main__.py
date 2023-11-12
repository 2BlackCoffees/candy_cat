"""
All start here
First install:
python3 -m pip install -r candy_cat/requirements.txt
"""
from services.application_service import start
import cProfile
import pstats
if __name__ == "__main__":
    enable_profiling = False
    profiler: cProfile.Profile = None
    if enable_profiling:
        profiler = cProfile.Profile()
        profiler.enable()
    start()
    if enable_profiling:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('tottime')
        stats.print_stats()
