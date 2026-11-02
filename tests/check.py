#!/usr/bin/env python3
"""Check the single-file daemon's parser and scheduler without starting it."""
from pathlib import Path
import subprocess
import tempfile

source = (Path(__file__).resolve().parents[1] / "main.swift").read_text()


def section(start, end):
    return source.split(start, 1)[1].split(end, 1)[0]


# Compile the actual parser and scheduler, replacing only action execution.
program = "import Cocoa\n"
program += "struct Config:" + section("struct Config:", "let configURL =")
program += "let KEY_CODES:" + section("let KEY_CODES:", "var actions:")
program += "\nfunc err(_ text: String) {}\nfunc log(_ text: String) {}\n"
program += "func parse(_ config: Config) -> [String: [GestureAction]] {\n"
program += "var actions:" + section("var actions:", "if actions.isEmpty")
program += "return actions\n}\n"
program += r'''
func parseAction(_ action: String) -> [GestureAction]? {
    let json = """
    {"manipulators":[{"from":{"gesture":"three_finger_swipe_left"},"to":[\(action)]}]}
    """
    return parse(try! JSONDecoder().decode(Config.self, from: Data(json.utf8)))["three_finger_swipe_left"]
}
let keys = parseAction(#"{"key_code":"tab","modifiers":["left_command","shift"]}"#)!
if case let .key(code, flags) = keys[0] {
    precondition(code == 48 && flags == [.maskCommand, .maskShift])
} else { fatalError("keyboard action changed") }
let urls = parseAction(#"{"url":"example://action","bundle_id":"org.example.app"}"#)!
if case let .url(url, bundleID) = urls[0] {
    precondition(url == "example://action" && bundleID == "org.example.app")
} else { fatalError("URL action not parsed") }
for invalid in [
    #"{}"#,
    #"{"key_code":"invalid"}"#,
    #"{"key_code":"tab","modifiers":["invalid"]}"#,
    #"{"url":"example://action"}"#,
    #"{"bundle_id":"org.example.app"}"#,
    #"{"url":"relative","bundle_id":"org.example.app"}"#,
    #"{"url":"example://action","bundle_id":""}"#,
    #"{"url":"example://action","bundle_id":"org.example.app","key_code":"tab"}"#,
    #"{"url":"example://action","bundle_id":"org.example.app","modifiers":[]}"#
] { precondition(parseAction(invalid) == nil, "invalid action accepted: \(invalid)") }
precondition(parseAction(#"{"key_code":"tab"},{"url":"example://action","bundle_id":"org.example.app"}"#)!.count == 2)

let started = DispatchSemaphore(value: 0)
let release = DispatchSemaphore(value: 0)
var performedKeys = 0
var performedURLs = 0
func perform(_ seq: [GestureAction]) {
    if seq.contains(where: { if case .url = $0 { return true }; return false }) {
        performedURLs += 1
        started.signal()
        precondition(release.wait(timeout: .now() + 5) == .success)
    } else { performedKeys += 1 }
}
var actions: [String: [GestureAction]] = ["url": urls, "key": keys, "mixed": keys + urls]
'''
program += "let actionQueue =" + section("let actionQueue =", "// Gesture state.")
program += r'''
fire("url")
precondition(started.wait(timeout: .now() + 5) == .success)
for _ in 0..<100 { fire("url"); fire("mixed") }
fire("key")
fire("unmapped")
precondition(performedKeys == 1, "URL action blocked keyboard gesture")
release.signal()
actionQueue.sync {}
precondition(performedURLs == 1, "busy gestures accumulated stale actions")
fire("mixed")
precondition(started.wait(timeout: .now() + 5) == .success, "URL slot was not released")
release.signal()
actionQueue.sync {}
precondition(performedURLs == 2)
print("Configuration and slow-target scheduling checks passed")
'''
with tempfile.TemporaryDirectory(prefix="threefinger-check-") as directory:
    root = Path(directory)
    swift = root / "main.swift"
    swift.write_text(program)
    binary = root / "check"
    subprocess.run(["swiftc", "-O", "-module-cache-path", str(root / "cache"),
                    str(swift), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True, timeout=15)
