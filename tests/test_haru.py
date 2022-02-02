import sys

import pytest
import haru


@pytest.mark.asyncio
async def test_communicator() -> None:
    communicator = haru.Communicator()
    output = await communicator.run(
        sys.executable, "-c", stdin="print('test')", stdout=haru.PIPE
    )
    assert output.rstrip() == "test"
