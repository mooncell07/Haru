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
    output = await process.execute()
    if output:
        assert output.rstrip() == "test"
    else:
        assert False

@pytest.mark.asyncio
async def test_run_in_shell() -> None:
    communicator = haru.Communicator(shell=True)
    process = await communicator.create_process("echo test", stdout=haru.PIPE)
    assert isinstance(process, haru.Process)
    output = await process.execute()
    if output:
        assert output.rstrip() == "test"
    else:
        assert False

@pytest.mark.asyncio
async def test_cm_and_sync() -> None:
    with haru.Communicator(shell=True) as communicator:
        process1 = await communicator.create_process("sleep 2;echo process1")
        process2 = await communicator.create_process("echo process2", stdout=haru.PIPE)

        data1 = await process1.execute()
        data2 = await process2.execute()

        assert data1 is None
        assert isinstance(data2, str)
        assert data2.rstrip() == "process2"
