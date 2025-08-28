from typing import List, Tuple

# --- opcodes ---
OP_MAP = {'=': 0b00, '-': 0b01, '+': 0b10}
REV_OP = {v: k for k, v in OP_MAP.items()}

# --- unsigned LEB128 varint helpers ---
def uvarint_encode(x: int) -> bytes:
    if x < 0:
        raise ValueError("uvarint must be non-negative")
    out = bytearray()
    while True:
        b = x & 0x7F
        x >>= 7
        if x:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)

def uvarint_decode(data: bytes, offset: int) -> Tuple[int, int]:
    x = 0
    shift = 0
    while True:
        if offset >= len(data):
            raise ValueError("truncated varint")
        b = data[offset]
        offset += 1
        x |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            return x, offset
        shift += 7
        if shift > 63:
            raise ValueError("varint too large")

# --- pack/unpack 2-bit opcodes, 4 per byte, little-endian within byte ---
def pack_opcodes(ops: List[str]) -> bytes:
    out = bytearray()
    cur = 0
    bitpos = 0
    for i, op in enumerate(ops):
        code = OP_MAP[op]
        cur |= (code & 0b11) << bitpos
        bitpos += 2
        if (i & 3) == 3:  # every 4 ops -> flush a byte
            out.append(cur)
            cur = 0
            bitpos = 0
    if (len(ops) & 3) != 0:
        out.append(cur)
    return bytes(out)

def unpack_opcodes(buf: bytes, n: int) -> List[str]:
    ops = []
    idx = 0
    for _ in range((n + 3) // 4):
        b = buf[idx]
        idx += 1
        for k in range(4):
            if len(ops) == n:
                break
            code = (b >> (2 * k)) & 0b11
            if code not in REV_OP:
                raise ValueError(f"invalid opcode bits {code:02b}")
            ops.append(REV_OP[code])
    return ops

# --- main encode/decode ---
def encode_path(path: List[Tuple[str, object]]) -> bytes:
    """
    path example: [('=', 7), ('+', 'new '), ('=', 6), ('-', 4)]
    """
    n = len(path)
    if not (0 <= n <= 65535):
        raise ValueError("number of tuples must fit in one byte (0..255)")

    ops = [op for op, _ in path]
    opcode_bytes = pack_opcodes(ops)

    # operands stream + collect text blob
    operands = bytearray()
    texts = []
    for op, val in path:
        if op in ('=', '-'):
            if not isinstance(val, int) or val < 0:
                raise ValueError(f"Operand for {op} must be non-negative int")
            operands += uvarint_encode(val)
        elif op == '+':
            if not isinstance(val, (bytes, str)):
                raise ValueError("Operand for + must be str or bytes")
            b = val if isinstance(val, bytes) else val.encode('utf-8')
            operands += uvarint_encode(len(b))
            texts.append(b)
        else:
            raise ValueError(f"Unknown op {op}")

    blob = b''.join(texts)
    n_bytes = n.to_bytes(2, byteorder="little", signed=False)
    return n_bytes + opcode_bytes + bytes(operands) + blob

def decode_path(data: bytes) -> List[Tuple[str, object]]:
    """
    Returns path in the same format:
      '=' and '-' carry integer counts,
      '+' carries UTF-8 decoded string (falls back to raw bytes if decoding fails).
    """
    if not data:
        raise ValueError("empty input")
    n = int.from_bytes(data[:2], byteorder="little", signed=False)
    off = 2

    opcode_bytes_len = (n + 3) // 4
    if off + opcode_bytes_len > len(data):
        raise ValueError("truncated opcode section")
    ops = unpack_opcodes(data[off:off+opcode_bytes_len], n)
    off += opcode_bytes_len

    # First pass: read operands (varints), count total text bytes
    text_lengths = []
    operands = []
    for op in ops:
        val, off = uvarint_decode(data, off)
        if op == '+':
            text_lengths.append(val)
            operands.append(('len+', val))
        else:
            operands.append((op, val))

    # Second pass: slice out concatenated text blob
    texts = []
    for L in text_lengths:
        if off + L > len(data):
            raise ValueError("truncated text blob")
        texts.append(data[off:off+L])
        off += L

    # Rebuild path (consume texts in order)
    text_i = 0
    path: List[Tuple[str, object]] = []
    for (op, val) in operands:
        if op == 'len+':
            b = texts[text_i]
            text_i += 1
            try:
                path.append(('+', b.decode('utf-8')))
            except UnicodeDecodeError:
                path.append(('+', b))  # keep as bytes if not valid UTF-8
        elif op in ('=', '-'):
            path.append((op, val))
        else:
            raise RuntimeError("unexpected state")
    return path

# --- quick demo ---
if __name__ == "__main__":
    original = [('=', 7), ('+', 'new '), ('=', 6), ('-', 4), ('+', 'hi')]
    blob = encode_path(original)
    restored = decode_path(blob)
    assert restored == original