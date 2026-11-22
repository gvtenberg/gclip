#!/usr/bin/env python3
# Puts files on the clipboard in several formats at once (Files/Nautilus, Firefox and text editors).
# The extension can only offer one format; this helper uses X11 (XWayland), which does not need focus,
# and keeps running until another copy replaces it.
# Usage: files-clipboard.py file:///path/a file:///path/b
import os
import sys
from urllib.parse import unquote, urlparse

os.environ['GDK_BACKEND'] = 'x11'
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gdk, GLib, Gtk

uris = [u for u in sys.argv[1:] if u]
if not uris:
    sys.exit(1)
paths = '\n'.join(unquote(urlparse(u).path) for u in uris).encode()
formats = {
    'x-special/gnome-copied-files': ('copy\n' + '\n'.join(uris)).encode(),
    'text/uri-list': ('\r\n'.join(uris) + '\r\n').encode(),
    'text/plain;charset=utf-8': paths,
    'text/plain': paths,
}

Gtk.init()
clipboard = Gdk.Display.get_default().get_clipboard()
provider = Gdk.ContentProvider.new_union(
    [Gdk.ContentProvider.new_for_bytes(m, GLib.Bytes.new(d)) for m, d in formats.items()])
loop = GLib.MainLoop()


def on_clipboard_changed(*_):
    # another program copied something: this helper is no longer needed
    if not clipboard.is_local():
        loop.quit()


clipboard.set_content(provider)
clipboard.connect('changed', on_clipboard_changed)
GLib.timeout_add_seconds(12 * 3600, loop.quit)  # safety: do not keep running forever
loop.run()
