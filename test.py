from relay_controller import CapRelay
from time import sleep

relay = CapRelay([22, 23, 24, 25], [1, 1, 0, 0], [0, 0, 1, 1])

relay.set_state("charge")

sleep(1)

relay.set_state("dump")

sleep(1)

relay.set_state("null")

sleep(1)

relay.close_all()

sleep(1)