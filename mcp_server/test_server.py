#!/usr/bin/env python3
"""
Local integration test for the GSA KWM2 MCP server.
Drives the server process over stdin/stdout using raw MCP JSON-RPC messages.
Covers: initialization, tools/list (discovery), and all three tool calls.
"""
import json
import subprocess
import sys
import textwrap


def send(proc, msg: dict) -> dict:
    """Send one JSON-RPC message and read one response."""
    raw = json.dumps(msg) + "\n"
    proc.stdin.write(raw.encode())
    proc.stdin.flush()
    line = proc.stdout.readline()
    return json.loads(line.decode())


def check(label: str, resp: dict, *, expect_result_key: str = None):
    if "error" in resp:
        print(f"  FAIL [{label}]: error = {resp['error']}")
        return False
    result = resp.get("result", {})
    print(f"  PASS [{label}]")
    if expect_result_key:
        val = result.get(expect_result_key)
        print(f"       {expect_result_key} = {json.dumps(val)[:200]}")
    return True


def main():
    print("Starting MCP server process …")
    proc = subprocess.Popen(
        [sys.executable, "mcp_server/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    ok_all = True

    # ------------------------------------------------------------------
    # 1. Initialize
    # ------------------------------------------------------------------
    print("\n[1] Initialize")
    resp = send(proc, {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"},
        },
    })
    ok_all &= check("initialize", resp)

    # Send initialized notification (no response expected)
    proc.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
    proc.stdin.flush()

    # ------------------------------------------------------------------
    # 2. Tool discovery — tools/list
    # ------------------------------------------------------------------
    print("\n[2] Tool discovery (tools/list)")
    resp = send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    ok = check("tools/list", resp)
    ok_all &= ok
    if ok:
        tools = resp["result"].get("tools", [])
        names = [t["name"] for t in tools]
        print(f"       tools = {names}")
        expected = {
            "gsa_kwm2_current_weather",
            "gsa_kwm2_programming_joke",
            "gsa_kwm2_unit_converter",
        }
        missing = expected - set(names)
        if missing:
            print(f"  FAIL [tools/list]: missing tools = {missing}")
            ok_all = False
        else:
            print("       All three gsa_kwm2_* tools present ✓")

    # ------------------------------------------------------------------
    # 3. Call gsa_kwm2_current_weather
    # ------------------------------------------------------------------
    print("\n[3] gsa_kwm2_current_weather(city='London')")
    resp = send(proc, {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "gsa_kwm2_current_weather", "arguments": {"city": "London"}},
    })
    ok = check("gsa_kwm2_current_weather", resp)
    ok_all &= ok
    if ok:
        content = resp["result"].get("content", [])
        text = content[0]["text"] if content else "(empty)"
        print(f"       result = {text!r}")

    # ------------------------------------------------------------------
    # 4. Call gsa_kwm2_programming_joke
    # ------------------------------------------------------------------
    print("\n[4] gsa_kwm2_programming_joke()")
    resp = send(proc, {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {"name": "gsa_kwm2_programming_joke", "arguments": {}},
    })
    ok = check("gsa_kwm2_programming_joke", resp)
    ok_all &= ok
    if ok:
        content = resp["result"].get("content", [])
        text = content[0]["text"] if content else "(empty)"
        print(f"       result = {text!r}")

    # ------------------------------------------------------------------
    # 5. Call gsa_kwm2_unit_converter — valid conversion
    # ------------------------------------------------------------------
    print("\n[5] gsa_kwm2_unit_converter(100, 'km', 'miles')")
    resp = send(proc, {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "gsa_kwm2_unit_converter",
            "arguments": {"value": 100.0, "from_unit": "km", "to_unit": "miles"},
        },
    })
    ok = check("gsa_kwm2_unit_converter km->miles", resp)
    ok_all &= ok
    if ok:
        content = resp["result"].get("content", [])
        text = content[0]["text"] if content else "(empty)"
        print(f"       result = {text!r}")
        if "62.1" not in text:
            print("  WARN: expected ~62.1 miles in result")

    # ------------------------------------------------------------------
    # 6. Call gsa_kwm2_unit_converter — celsius to fahrenheit
    # ------------------------------------------------------------------
    print("\n[6] gsa_kwm2_unit_converter(0, 'celsius', 'fahrenheit')")
    resp = send(proc, {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "gsa_kwm2_unit_converter",
            "arguments": {"value": 0.0, "from_unit": "celsius", "to_unit": "fahrenheit"},
        },
    })
    ok = check("gsa_kwm2_unit_converter celsius->fahrenheit", resp)
    ok_all &= ok
    if ok:
        content = resp["result"].get("content", [])
        text = content[0]["text"] if content else "(empty)"
        print(f"       result = {text!r}")
        if "32" not in text:
            print("  WARN: expected 32°F for 0°C")

    # ------------------------------------------------------------------
    # 7. Call gsa_kwm2_unit_converter — unsupported pair
    # ------------------------------------------------------------------
    print("\n[7] gsa_kwm2_unit_converter(5, 'parsecs', 'furlongs') — expect error string")
    resp = send(proc, {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "gsa_kwm2_unit_converter",
            "arguments": {"value": 5.0, "from_unit": "parsecs", "to_unit": "furlongs"},
        },
    })
    ok = check("gsa_kwm2_unit_converter unsupported", resp)
    ok_all &= ok
    if ok:
        content = resp["result"].get("content", [])
        text = content[0]["text"] if content else "(empty)"
        print(f"       result = {text!r}")
        if "Unsupported" not in text:
            print("  WARN: expected 'Unsupported' in error response")

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    proc.terminate()
    proc.wait(timeout=5)
    print("\n" + ("=" * 60))
    print("ALL TESTS PASSED ✓" if ok_all else "SOME TESTS FAILED ✗")
    print("=" * 60)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
