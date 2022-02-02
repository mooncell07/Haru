import subprocess
import sys

import pytest
from haru import Communicator


@pytest.mark.asyncio
async def test_communicator():
    comm = Communicator()
    output = await comm.run(
        sys.executable, "-c", stdin="print('test')", stdout=subprocess.PIPE
    )
    assert output == "test\n"
