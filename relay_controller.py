from gpiozero import LEDBoard
from time import sleep
from typing import List, Dict, Optional, Union


class RelayController:
    """
    Controls relay boards connected to GPIO pins
    """

    def __init__(self, relay_pins: List[int]):
        self.relay_pins = relay_pins
        self.num_relays = len(relay_pins)
        self._board = LEDBoard(*relay_pins)

        self.open_all()

        print(f"RelayController initialized with {self.num_relays} relays on pins {relay_pins}")

    def close(self, relay_num: int) -> None:
        """
        Close a relay (turns it on)
        """
        self._validate_relay_number(relay_num)
        self._board[relay_num].off()
        print(f"Relay {relay_num} closed (on)")

    def open(self, relay_num: int) -> None:
        """
        Open a relay (turns it off)
        """
        self._validate_relay_number(relay_num)
        self._board[relay_num].on()
        print(f"Relay {relay_num} open (off)")

    def close_all(self) -> None:
        """
        Sequentially close all relays
        """
        for relay in self._board:
            relay.off()
        print("All relays closed")
    
    def open_all(self) -> None:
        """
        Sequentially open all relays
        """
        for relay in self._board:
            relay.on()
        print("All relays opened")

    def get_state(self, relay_num: int) -> bool:
        """
        Get the current state of a relay pin
        """
        self._validate_relay_number(relay_num)
        return not self._board[relay_num].is_lit

    def _validate_relay_number(self, relay_num: int) -> None:
        """
        Validate that a relay number is within range
        """
        if not 0 <= relay_num < self.num_relays:
            raise ValueError(f"Relay number must be between 0 and {self.num_relays-1}")


class CapRelay(RelayController):
    """
    Class specifically for controlling CUTE's capacitor charge/dump relays
    """
    
    def __init__(self,
                relay_pins: List[int],
                chg_config: List[int],
                dmp_config: List[int]):

        super().__init__(relay_pins)

        # Validate configurations
        if len(chg_config) != len(dmp_config):
            raise ValueError(f"chg_config and dmp_config must use the same number of GPIO pins")

        if len(relay_pins) != len(chg_config):
            raise ValueError(f"chg/dmp configs require {len(chg_config)} GPIO pins to be allocated")

        self.chg_config = chg_config
        self.dmp_config = dmp_config
        self.current_state = "null"

        self.null_state = [0] * len(relay_pins)
        self.set_state("null")

        print(f"CapRelay initialized with {len(relay_pins)} relays on pins {relay_pins}")
        print(f"  Charge configuration: {chg_config}")
        print(f"  Dump configuration: {dmp_config}")
        
    def set_state(self, state_name: str) -> None:
        """
        Switch to predefined state
        """

        if state_name.lower() == "charge":
            config = self.chg_config
        elif state_name.lower() == "dump":
            config = self.dmp_config
        elif state_name.lower() == "null":
            config = self.null_state
        else:
            raise ValueError(f"Invalid state: {state_name}")

        # Apply configuration
        for relay_num, should_be_closed in enumerate(config):
            if should_be_closed == 1:
                self.close(relay_num)
            elif should_be_closed == 0:
                self.open(relay_num)
            else:
                raise ValueError(f"Invalid relay state {should_be_closed} at position {relay_num}")
        
        self.current_state = state_name.lower()
        print(f"Switched to {state_name} state: {config}")

    def get_state_info(self) -> Dict:
        """
        Gets information about the current state. Returns dict
        """

        return {
            "current_state": self.current_state,
            "configuration": self.get_state_config(),
            "relay_states": [1 if self.get_state(i) else 0 for i in range(self.num_relays)],
            "pins": self.relay_pins
        }

    