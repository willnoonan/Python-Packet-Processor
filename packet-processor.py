"""
Author: william noonan
"""

class Packet:
    def __init__(self, message_id: int, sequence: int, total_packets: int, payload: str):
        self.message_id = message_id
        self.sequence = sequence
        self.total_packets = total_packets
        self.payload = payload

    def __str__(self):
        payload = f'"{self.payload}"' if type(self.payload) is str else self.payload
        return f"""Packet(message_id={self.message_id}, sequence={self.sequence}, total_packets={self.total_packets}, payload={payload})"""

    def __repr__(self):
        return self.__str__()


class ProcessPacket:
    def __init__(self):
        self.packet_map = dict()  # {msg_id: list[Packet]}

    def process_packet(self, packet: Packet):

        msg_id = packet.message_id

        if msg_id < 0:
            raise ValueError("invalid message_id")

        if packet.sequence < 0:
            return ValueError("invalid sequence")

        if type(packet.payload) is not str:
            raise ValueError("invalid payload, must be a string")

        if packet.sequence + 1 > packet.total_packets:
            raise ValueError("packet's sequence index cannot exceed that allowed by its total_packets")

        # if msg_id never seen before, initialize list for it
        if msg_id not in self.packet_map:
            self.packet_map[msg_id] = [None] * packet.total_packets

        # what happens if new packet has different length than seen previously
        # policy: if new packet's total_packets is less than current list size, reject
        if packet.total_packets < len(self.packet_map[msg_id]):
            raise ValueError(f"total_packets cannot be less than that seen previously for message_id={packet.message_id}")

        # policy: if it's longer, allow it to extend packet_map list
        if packet.total_packets > len(self.packet_map[msg_id]):
            self.packet_map[msg_id].extend([None] * (packet.total_packets - len(self.packet_map[msg_id])))

        # put it in the dict
        # first check if this packet would overwrite
        if self.packet_map[msg_id][packet.sequence] is not None:
            pass  # todo policy: consider rejecting overwrites

        self.packet_map[msg_id][packet.sequence] = packet.payload

        # determine if full payload can be returned
        if not None in self.packet_map[msg_id]:
            # todo policy: consider not wiping msg_id
            res = " ".join(p for p in self.packet_map.pop(msg_id))
            return res

        return None


def main():
    s = ProcessPacket()

    packets = [
        Packet(1, 1, 2, "world"),
        Packet(1, 2, 3, "end"),
        Packet(1, 0, 4, None),
        Packet(1, 3, 3, "water"),
        Packet(1, 3, 4, "here"),
        Packet(0, 2, 3, "vehicle"),
        Packet(1, 0, 2, "hello"),
        Packet(1, 2, 4, "i'm"),
        Packet(1, 0, 4, "Hello"),
        Packet(1, 0, 4, "planet"),
    ]

    for p in packets:
        try:
            res = s.process_packet(p)
            print(f"Accepted packet: {p}")
            if res:
                print(f"Message completed for message_id={p.message_id}: {res}")
        except ValueError as e:
            print(f"Rejected packet: {p} -> ValueError: {e}")


if __name__ == '__main__':
    main()
