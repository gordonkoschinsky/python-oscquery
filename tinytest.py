import time

from tinyoscquery.osc_query_service import OSCQueryService
from tinyoscquery.shared.node import OSCQueryNode
from tinyoscquery.shared.osc_access import OSCAccess

if __name__ == "__main__":
    oscqs = OSCQueryService("Test-Service", 9020, 9020)
    print(oscqs.root_node)

    oscqs.add_node(
        OSCQueryNode("/testing/is/cool", value=99, access=OSCAccess.READONLY_VALUE)
    )

    print(oscqs.root_node)

    while True:
        time.sleep(1)
