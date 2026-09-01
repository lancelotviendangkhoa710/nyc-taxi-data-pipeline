import sys
from dbt.cli.main import dbtRunner, dbtRunnerResult

runner = dbtRunner()
res: dbtRunnerResult = runner.invoke(sys.argv[1:])
if not res.success:
    sys.exit(1)
