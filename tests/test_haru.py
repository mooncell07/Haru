import sys

import pytest
import haru


@pytest.mark.asyncio
async def test_shell_exec() -> None:
    communicator = haru.Communicator()
    output = await communicator.run(
        sys.executable, "-c", stdin="print('test')", stdout=haru.PIPE
    )
    assert output.rstrip() == "test"


@pytest.mark.asyncio
async def test_run_in_shell() -> None:
    communicator = haru.Communicator(shell=True)
    output = await communicator.run("echo test", stdout=haru.PIPE)
    assert output.rstrip() == "test"
