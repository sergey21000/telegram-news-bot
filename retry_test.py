import sys
import os

marker_file = "first_run_done"

if not os.path.exists(marker_file):
    print("❌ First run — simulating EmailNotArrivedYet, exit 111")
    open(marker_file, "w").close()
    sys.exit(111)
else:
    print("✅ Second run — success")
    sys.exit(0)
