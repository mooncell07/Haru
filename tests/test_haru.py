import sys

import pytest
import haru


@pytest.mark.asyncio
async def test_shell_exec() -> None:
    communicator = haru.Communicator()
    process = await communicator.create_process(
        sys.executable, "-c", stdin="print('test')", stdout=haru.PIPE
    )
    assert isinstance(process, haru.Process)


@pytest.mark.asyncio
async def test_run_in_shell() -> None:
    communicator = haru.Communicator(shell=True)
    process = await communicator.create_process("echo test", stdout=haru.PIPE)
    assert isinstance(process, haru.Process)
    output = await process.execute()
    assert output.rstrip() == "test"
