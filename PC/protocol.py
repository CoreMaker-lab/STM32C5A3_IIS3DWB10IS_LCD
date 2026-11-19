"""V1 little-endian raw XYZ protocol; CRC32 matches zlib."""
import struct
import zlib
import numpy as np
MAGIC = b'\xa5\x5a\xc3\x3c'
HEADER = struct.Struct('<4sBBHIIIHH')

def encode(raw, seq=0, fs=2500, first=0, flags=0):
    raw = np.asarray(raw, dtype='<i4').reshape(-1, 3)
    payload = raw.tobytes()
    data = HEADER.pack(MAGIC, 1, 1, len(payload), seq, fs, first, len(raw), flags) + payload
    return data + struct.pack('<I', zlib.crc32(data))

class Parser:
    def __init__(self):
        self.buf = bytearray()
        self.errors = 0
        self.text = bytearray()
    def feed(self, data):
        self.buf.extend(data)
        packets, logs = [], []
        def log_bytes(b):
            self.text.extend(b)
            while b'\n' in self.text:
                line, _, rest = self.text.partition(b'\n')
                self.text = bytearray(rest)
                logs.append(line.decode('utf-8', errors='replace').strip())
            if len(self.text) > 4096:
                self.text.clear()
        while True:
            pos = self.buf.find(MAGIC)
            if pos < 0:
                # Retain ONLY a possible partial binary magic prefix. A complete
                # ASCII ACK must not wait for some future packet to release its newline.
                keep=0
                for suffix in (3,2,1):
                    if len(self.buf)>=suffix and self.buf[-suffix:]==MAGIC[:suffix]:
                        keep=suffix;break
                n = len(self.buf)-keep
                log_bytes(self.buf[:n]); del self.buf[:n]
                break
            if pos:
                log_bytes(self.buf[:pos]); del self.buf[:pos]
            if len(self.buf) < HEADER.size:
                break
            _, ver, kind, length, seq, fs, first, count, flags = HEADER.unpack_from(self.buf)
            if ver != 1 or kind != 1 or not 1 <= count <= 256 or length != count*12 or not 1 <= fs <= 1000000:
                self.errors += 1; del self.buf[0]; continue
            size = HEADER.size + length + 4
            if len(self.buf) < size:
                break
            expected, = struct.unpack_from('<I', self.buf, size-4)
            if zlib.crc32(self.buf[:size-4]) != expected:
                self.errors += 1; del self.buf[0]; continue
            raw = np.frombuffer(bytes(self.buf[HEADER.size:size-4]), dtype='<i4').reshape(count, 3)
            packets.append((seq, fs, first, flags, raw))
            del self.buf[:size]
        return packets, logs

def spectrum(mg, fs):
    """One-sided Hann amplitude, mg; DC removed."""
    n = len(mg)
    if n < 8:
        return np.empty(0), np.empty((0, 3))
    w = np.hanning(n)
    y = mg - mg.mean(axis=0)
    amplitude = np.abs(np.fft.rfft(y*w[:, None], axis=0))*2/w.sum()
    amplitude[0] *= .5
    if n % 2 == 0:
        amplitude[-1] *= .5
    return np.fft.rfftfreq(n, 1/fs), amplitude
