import json
from difflib import SequenceMatcher
from typing import List, Tuple, Union
from diff_encoder import encode_path, decode_path

# PatchOp = Tuple[str, str]  # ('=', text) copy from old, ('-', text) delete from old, ('+', text) insert new text

from typing import List, Tuple, Union

PatchOp = Tuple[str, Union[int, str]]

def merge_patch_ops(
    patch: List[PatchOp],
    old: str,
    new: str,
    max_eq_fold: int = 1,   # fold '=' of length <= this into the replacement
    max_window_ops: int = 32  # safety cap so we don't scan forever
) -> List[PatchOp]:
    """
    Merge small alternating sequences like ('-', 2), ('+', 'n'), ('=', 1), ('+', 'w')
    into ('-', 3), ('+', 'new'), using old/new strings to materialize '+' text.
    """
    merged: List[PatchOp] = []

    i = 0
    old_pos = 0
    new_pos = 0

    # Helper to append op while coalescing neighbors of same type (nice & compact)
    def push(op: PatchOp):
        nonlocal merged
        if not merged:
            merged.append(op)
            return
        t, v = op
        pt, pv = merged[-1]
        if t == pt:
            if t in ('=', '-'):
                merged[-1] = (t, int(pv) + int(v))
            else:  # '+'
                merged[-1] = (t, str(pv) + str(v))
        else:
            merged.append(op)

    # First pass: walk the original patch and keep old_pos/new_pos in sync
    # We'll build a list of ops with positions consumed, so we can then do the merging.
    # But to stay simple, we do merging on-the-fly whenever we meet '-'.
    while i < len(patch):
        t, v = patch[i]

        if t == '=':
            L = int(v)
            # Just advance pointers and push as-is
            push(('=', L))
            old_pos += L
            new_pos += L
            i += 1
            continue

        if t == '+':
            s = str(v)
            push(('+', s))
            new_pos += len(s)
            i += 1
            continue

        # t == '-'  => start a replacement window
        del_len = int(v)
        i += 1
        old_start = old_pos
        new_start = new_pos

        # Consume this initial deletion
        old_pos += del_len

        # We'll accumulate inserted text from `new`
        ins_text_parts: List[str] = []
        consumed_ops = 1  # we already consumed one '-'

        # Try to greedily absorb patterns of { '-', '+', '='<=max_eq_fold }
        while i < len(patch) and consumed_ops < max_window_ops:
            nt, nv = patch[i]

            if nt == '-':
                d = int(nv)
                del_len += d
                old_pos += d
                i += 1
                consumed_ops += 1

            elif nt == '+':
                s = str(nv)
                # We trust '+' carries the correct slice from `new`, but re-derive to be safe
                # by slicing from `new_pos`. This ensures consistency even if upstream changes format.
                expected = new[new_pos:new_pos+len(s)]
                # If upstream '+' text matches the new slice, take from new for robustness
                # (It should match; if not, we still append s to avoid corruption.)
                ins_text_parts.append(expected if expected == s else s)
                new_pos += len(s)
                i += 1
                consumed_ops += 1

            elif nt == '=':
                k = int(nv)
                if k <= max_eq_fold:
                    # Fold the tiny keep into the replacement:
                    # delete those chars from old and insert the same # of chars from new
                    del_len += k
                    ins_text_parts.append(new[new_pos:new_pos+k])
                    old_pos += k
                    new_pos += k
                    i += 1
                    consumed_ops += 1
                else:
                    # Stop at a larger '=' to avoid over-absorbing
                    break
            else:
                break

        # Build the merged replacement
        ins_text = ''.join(ins_text_parts)

        # If the entire window had no actual insertion (rare, but possible if only deletions),
        # emit just the deletion. Otherwise emit both.
        if del_len > 0:
            push(('-', del_len))
        if ins_text:
            push(('+', ins_text))

        # Done with this replacement window; loop continues

    # Final clean-up pass: remove no-op ops (length 0) and coalesce neighbors again
    cleaned: List[PatchOp] = []
    for t, v in merged:
        if t in ('=', '-') and int(v) == 0:
            continue
        if t == '+' and len(str(v)) == 0:
            continue
        if cleaned and cleaned[-1][0] == t:
            # merge neighbors
            pt, pv = cleaned[-1]
            if t in ('=', '-'):
                cleaned[-1] = (t, int(pv) + int(v))
            else:
                cleaned[-1] = (t, str(pv) + str(v))
        else:
            cleaned.append((t, v))

    return cleaned


def generate_patch(old: str, new: str, print_flag: bool=False, compact: bool=False) -> List[PatchOp]:
    """Generate a compact patch transforming old -> new.

    The patch is a sequence of operations:
      '=' : keep text (verifies against old, not stored by reference)
      '-' : delete text (present in old, skipped in output)
      '+' : insert new text (not present in old)

    This representation is simple, streaming-friendly, and fully reversible.
    """
    if old is None:
        old = ''
    if new is None:
        new = ''

    sm = SequenceMatcher(a=old, b=new, autojunk=False)
    raw_ops: List[PatchOp] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            raw_ops.append(('=', i2 - i1))
        elif tag == 'insert':
            raw_ops.append(('+', new[j1:j2]))
        elif tag == 'delete':
            raw_ops.append(('-', i2 - i1))
        elif tag == 'replace':
            if i1 != i2:
                raw_ops.append(('-', i2 - i1))
            if j1 != j2:
                raw_ops.append(('+', new[j1:j2]))
        else:
            raise ValueError(f'Unknown tag {tag}')
        
    if compact:
        raw_ops = merge_patch_ops(raw_ops, old, new)

    if print_flag:
        print(f"{raw_ops=}")
    return raw_ops


import json, base64
from typing import List, Tuple, Union

# assuming you already have: PatchOp, encode_path, decode_path

def serialize_patch(patch: List[PatchOp], encode: bool = False) -> str:
    """Serialize patch: JSON string by default; if encode=True, Base64 of binary encoder."""
    if encode:
        blob = encode_path(patch)                  # bytes
        return base64.b64encode(blob).decode("ascii")  # always str
        # return blob
    return json.dumps(patch, ensure_ascii=False)       # always str

def deserialize_patch(data: str) -> List[PatchOp]:
    """
    Deserialize from JSON string; if that fails, treat input as Base64 of binary.
    Ensures:
      - '=' and '-' values are ints
      - '+' values are str
    """
    # Try JSON first
    try:
        raw = json.loads(data)
        assert isinstance(raw, list)
        return [(op, val) for op, val in raw]
        # out: List[PatchOp] = []
        # for elem in raw:
        #     assert isinstance(elem, (list, tuple)) and len(elem) == 2
        #     op, val = elem[0], elem[1]
        #     assert op in ('=', '-', '+')
        #     if op in ('=', '-'):
        #         # keep as int; coerce if it accidentally came as str
        #         if isinstance(val, str):
        #             # allow numeric strings like "12"
        #             val = int(val) if val.isdigit() else int(float(val))
        #         elif not isinstance(val, int):
        #             val = int(val)
        #         out.append((op, val))
        #     else:  # '+'
        #         # force to str
        #         out.append((op, val if isinstance(val, str) else str(val)))
        # return out
    except Exception:
        # Fallback: Base64 -> binary -> decode_path; normalize '+' to str
        blob = base64.b64decode(data, validate=True)
        decoded = decode_path(blob)
        normalized: List[PatchOp] = []
        for op, val in decoded:
            if op in ('=', '-'):
                # ensure int
                if isinstance(val, int):
                    normalized.append((op, val))
                else:
                    normalized.append((op, int(val)))
            else:  # '+'
                # ensure str (UTF-8 if bytes; else str())
                if isinstance(val, (bytes, bytearray)):
                    try:
                        normalized.append(('+', val.decode('utf-8')))
                    except UnicodeDecodeError:
                        normalized.append(('+', val.decode('latin1')))
                else:
                    normalized.append(('+', val if isinstance(val, str) else str(val)))
        return normalized

# def deserialize_patch(data: Union[str, bytes, bytearray]) -> List[PatchOp]:
#     """Try JSON first; if it fails or input is bytes, fall back to binary decode."""
#     if isinstance(data, (bytes, bytearray, memoryview)):
#         return decode_path(bytes(data))
#     raw = json.loads(data)
#     assert isinstance(raw, list)
#     return [(op, val) for op, val in raw]
    
def apply_patch(old: str, patch: List[PatchOp]) -> str:
    """Reconstruct new string from old and patch."""
    if old is None:
        old = ''
    out_parts: List[str] = []
    idx = 0
    for op, value in patch:
        if op == '=':
            # Must match old
            seg = old[idx: idx + value]
            out_parts.append(seg)
            idx += value
        elif op == '-':
            # Skip over deleted part (must match)
            idx += value
        elif op == '+':
            out_parts.append(value)
        else:
            raise ValueError(f'Unknown op {op}')
    return ''.join(out_parts)

# --- Pandas helpers -------------------------------------------------------

def add_patch_column(df, old_col='old_contents', new_col='new_contents', patch_col='new_patch', encode=False):
    """Add a column containing serialized patch replacing new_col (optionally).

    The DataFrame must contain old_col and new_col. The function creates patch_col.
    It does NOT drop new_col by default so you can verify correctness first.
    """
    try:
        import pandas as pd  # type: ignore
    except Exception as e:  # pragma: no cover
        raise ImportError('pandas is required for add_patch_column') from e
    assert old_col in df.columns and new_col in df.columns
    patches = []
    for old, new in zip(df[old_col].tolist(), df[new_col].tolist()):
        patch = generate_patch(str(old) if old is not None else '', str(new) if new is not None else '')
        patches.append(serialize_patch(patch, encode=encode))
    df[patch_col] = patches
    return df


def reconstruct_from_patch(df, old_col='old_contents', patch_col='new_patch', out_col='reconstructed_new'):
    """Reconstruct new contents into out_col using old_col + patch_col."""
    assert old_col in df.columns and patch_col in df.columns
    out = []
    for old, patch_s in zip(df[old_col].tolist(), df[patch_col].tolist()):
        patch = deserialize_patch(patch_s)
        out.append(apply_patch(str(old) if old is not None else '', patch))
    df[out_col] = out
    return df


def verify_patch_roundtrip(df, new_col='new_contents', reconstructed_col='reconstructed_new') -> int:
    if new_col not in df.columns or reconstructed_col not in df.columns:
        raise KeyError('Expected both original new and reconstructed columns')
    mismatches = (df[new_col] != df[reconstructed_col]).sum()
    return mismatches

__all__ = [
    'generate_patch', 'apply_patch', 'serialize_patch', 'deserialize_patch',
    'add_patch_column', 'reconstruct_from_patch', 'verify_patch_roundtrip'
]
