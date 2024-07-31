from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

import poetry_version

__version__ = poetry_version.extract(source_file=__file__)


class Historic:
    state: str  # état courant
    reading: str  # ce que la machine lit
    position: int  # la position de la machine sur le ruban (relatif au champs memory)
    memory: str  # l'état actuel du ruban (avec symboles vide à gauche et à droite, contrairement à l'output de la machine qui doit être renvoyé)
    transition: str  # la transition choisit dans la table (une string ou un dict donc) pour choisir le prochain état et le symbole à écrire.

    def __init__(self) -> None:
        self.historic = []

    def update(self, state, reading, position, memory, transition):
        self.historic.append(self.getDict())
        self.state = state
        self.reading = reading
        self.position = position
        self.memory = memory
        self.transition = transition

    # def __str__(self) -> str:
    #     return repr(self.historic)

    def getDict(self):
        return {
            "state": self.state,
            "reading": self.reading,
            "position": self.position,
            "memory": self.memory,
            "transition": self.transition,
        }


def repl(string, char, index):
    """
    The function replaces a character in a string at a specified index and returns the modified string.
    """
    res = list(string)
    res[index] = char
    return "".join(res)


def compute_machine(
    machine: Dict, input_: str, steps: Optional[int] = None
) -> Tuple[str, List, bool]:
    final_states = machine["final states"]
    table = machine["table"]
    blank = machine["blank"]
    histo = Historic()
    current_state = histo.state = machine["start state"]
    current_position = histo.position = 0
    current_memory = histo.memory = input_
    current_reading = histo.reading = input_[0]
    current_transition = histo.transition = table[current_state][current_reading]
    i = 0
    while (current_state not in final_states) or (
        steps is not None and i < steps
    ):  # pragma: no branch
        if type(current_transition) is dict:
            try:
                current_state = current_transition["L"]
            except KeyError:
                current_state = current_transition["R"]
            try:
                current_memory = repl(
                    current_memory, current_transition["write"], current_position
                )
            except KeyError:
                pass  # If no write in the transition
            current_position += 1 if "R" in dict(current_transition).keys() else -1
        else:
            current_position += 1 if "R" in current_transition else -1
        if len(current_memory) <= current_position:
            current_memory += blank
        elif current_position < 0:
            current_memory = blank + current_memory
            current_position = 0
        current_reading = current_memory[current_position]
        try:
            current_transition = table[current_state][current_reading]
        except KeyError:
            # if current_state not in final_states:
            #     return histo.memory.strip(), histo.historic, False
            pass
        histo.update(
            current_state,
            current_reading,
            current_position,
            current_memory,
            current_transition,
        )
        i += 1
    return histo.memory.strip(blank), histo.historic, True


def run_turing_machine(
    machine: Dict, input_: str, steps: Optional[int] = None
) -> Tuple[str, List, bool]:
    return compute_machine(machine, input_, steps)
