"""
unicode_tag_decoder.py
detect hidden data in mouse_recorder.py so we,
Extract and decode hidden Unicode TAG characters
from mouse_recorder.py ( file).
Also includes optional encode demonstration.
"""

def extract_hidden_tags(filename):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    hidden_values = [ord(c) for c in text if ord(c) > 0xE0000]

    return hidden_values


def decode_tags(hidden_values):
    decoded = ""

    for val in hidden_values:
        # Ignore START TAG and END TAG
        if val in (0xE0001, 0xE007F):
            continue

        # Decode only valid TAG block characters
        if 0xE0020 <= val <= 0xE007E:
            decoded += chr(val - 0xE0000)

    return decoded


def encode_to_tags(message):
    """
    Demonstration: how text would be encoded
    into Unicode TAG block.
    """
    encoded = []

    # Add START TAG
    encoded.append(chr(0xE0001))

    for ch in message:
        encoded.append(chr(ord(ch) + 0xE0000))

    # Add END TAG
    encoded.append(chr(0xE007F))

    return "".join(encoded)


if __name__ == "__main__":

    filename = "mouse_recorder.py"

    print("Extracting hidden TAG characters...\n")

    hidden = extract_hidden_tags(filename)

    print("Raw hidden values:")
    print([hex(v) for v in hidden])
    print()

    decoded_message = decode_tags(hidden)

    print("Decoded hidden message:")
    print(decoded_message)
    print()

    print("---- Encoding Demo ----")
    demo = "HELLO"
    encoded_demo = encode_to_tags(demo)
    print("Example encoding of HELLO:")
    print([hex(ord(c)) for c in encoded_demo])