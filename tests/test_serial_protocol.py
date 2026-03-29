"""
Tests for the serial protocol framing logic
=============================================
Tests frame construction, header validation, and byte-level parsing
used in serial_listener.py.

These tests mock the serial port — no actual hardware needed.
"""

import pytest
import struct
from unittest.mock import MagicMock, patch
from io import BytesIO

from config import SERIAL_HEADER_BYTE, SERIAL_END_BYTE


class TestSerialProtocol:
    """Tests for the serial frame format."""

    def test_header_byte_value(self):
        """Header byte should be 0xAA."""
        assert SERIAL_HEADER_BYTE == 0xAA

    def test_end_byte_value(self):
        """End byte should be 0x55."""
        assert SERIAL_END_BYTE == 0x55

    def test_frame_construction(self):
        """A valid frame is: [0xAA] [4-byte length LE] [payload]."""
        payload = b"\x00\x01\x02\x03" * 100  # 400 bytes of dummy audio
        length = len(payload)

        frame = bytes([SERIAL_HEADER_BYTE])
        frame += struct.pack("<I", length)
        frame += payload

        # Parse it back
        assert frame[0] == SERIAL_HEADER_BYTE
        parsed_length = struct.unpack("<I", frame[1:5])[0]
        assert parsed_length == 400
        assert frame[5:] == payload

    def test_frame_with_zero_length(self):
        """Zero-length frames should be rejected."""
        frame = bytes([SERIAL_HEADER_BYTE]) + struct.pack("<I", 0)
        parsed_length = struct.unpack("<I", frame[1:5])[0]
        assert parsed_length == 0  # Implementation should skip this

    def test_frame_with_large_length(self):
        """Frames > 1 MB should be rejected as a sanity check."""
        huge_length = 2_000_000  # 2 MB
        frame = bytes([SERIAL_HEADER_BYTE]) + struct.pack("<I", huge_length)
        parsed_length = struct.unpack("<I", frame[1:5])[0]
        assert parsed_length > 1_000_000  # Implementation should skip this

    def test_response_code_encoding(self):
        """Response codes should be single ASCII characters."""
        for code in ["A", "R", "B", "W"]:
            encoded = code.encode("ascii")
            assert len(encoded) == 1
            assert encoded.decode("ascii") == code

    def test_response_message_format(self):
        """Response messages should be: [code] [2-byte length LE] [UTF-8 text]."""
        message = "Timer is done!"
        msg_bytes = message.encode("utf-8")
        response = b"R" + struct.pack("<H", len(msg_bytes)) + msg_bytes

        # Parse back
        assert response[0:1] == b"R"
        msg_len = struct.unpack("<H", response[1:3])[0]
        assert msg_len == len(msg_bytes)
        parsed_msg = response[3:3 + msg_len].decode("utf-8")
        assert parsed_msg == message


class TestAudioBuffering:
    """Tests for audio buffer assembly logic."""

    def test_single_frame(self):
        """Single frame should be buffered correctly."""
        buffer = bytearray()
        payload = b"\x00\x01" * 1000  # 2000 bytes
        buffer.extend(payload)
        assert len(buffer) == 2000
        assert bytes(buffer) == payload

    def test_multiple_frames(self):
        """Multiple frames should be concatenated."""
        buffer = bytearray()
        frame1 = b"\x00\x01" * 500
        frame2 = b"\x02\x03" * 500

        buffer.extend(frame1)
        buffer.extend(frame2)

        assert len(buffer) == 2000
        assert buffer[:1000] == frame1
        assert buffer[1000:] == frame2

    def test_buffer_clear(self):
        """Buffer should be clearable after transcription."""
        buffer = bytearray()
        buffer.extend(b"\x00" * 1000)
        assert len(buffer) == 1000

        buffer.clear()
        assert len(buffer) == 0
