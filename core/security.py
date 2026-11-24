import ctypes, stat, uuid
from ctypes import wintypes
from pathlib import Path

# Only ordinary local files; reject junctions, symlinks and network drives.
ALLOWED = {'.png','.jpg','.jpeg','.bmp','.webp','.gif','.pdf','.txt','.docx','.xlsx','.pptx','.csv','.py','.c','.cpp','.html','.css','.js','.zip','.mp4','.mp3'}
def local_path(path):
    try:
        p = Path(path)
        if not p.is_absolute() or not p.drive or str(p).startswith('\\\\'):
            return False
        if ctypes.windll.kernel32.GetDriveTypeW(str(p.anchor)) != 3:
            return False
        for part in (p, *p.parents):
            st = part.lstat()
            if getattr(st, 'st_file_attributes', 0) & (0x400 | 0x1000):
                return False
        return True
    except (OSError, ValueError):
        return False

def safe_file(path):
    try:
        p = Path(path)
        return (p.suffix.lower() in ALLOWED and not p.name.startswith(('.', '~'))
                and local_path(p) and stat.S_ISREG(p.lstat().st_mode)
                and not (getattr(p.lstat(), 'st_file_attributes', 0) & 6))
    except (OSError, ValueError):
        return False

def default_folders():
    # Resolve redirected Windows known folders without scanning the whole drive.
    ids = [
        ('374DE290-123F-4565-9164-39C4925E467B', 'Downloads'),
        ('B4BFCC3A-DB2C-424C-B029-7FE99A87C641', 'Desktop'),
        ('FDD39AD0-238F-46AF-ADB4-6C85480369C7', 'Documents'),
        ('33E28130-4E1E-4676-835A-98395C3BC3BB', 'Pictures'),
        ('B7BEDE81-DF94-4682-A7D8-57A52620B86F', 'Pictures/Screenshots'),
    ]
    get_path = ctypes.windll.shell32.SHGetKnownFolderPath
    get_path.argtypes = [ctypes.c_void_p, wintypes.DWORD, wintypes.HANDLE, ctypes.POINTER(ctypes.c_void_p)]
    get_path.restype = ctypes.c_long
    free = ctypes.windll.ole32.CoTaskMemFree
    free.argtypes = [ctypes.c_void_p]
    free.restype = None
    folders = []
    for guid, fallback in ids:
        raw = ctypes.create_string_buffer(uuid.UUID(guid).bytes_le)
        out = ctypes.c_void_p()
        try:
            if get_path(raw, 0, None, ctypes.byref(out)) == 0 and out.value:
                folders.append(Path(ctypes.wstring_at(out.value)))
        finally:
            if out.value: free(out)
        folders.append(Path.home() / fallback)
    return list(dict.fromkeys(folders))
