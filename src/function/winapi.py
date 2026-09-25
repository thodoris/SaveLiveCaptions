'''
Thin ctypes bindings for the few Win32 calls this project needs.

Declaring argtypes/restype matters on 64-bit Python: without them ctypes
truncates handles and pointer-sized parameters to 32-bit ints.
'''
import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

WM_QUIT = 0x0012
WM_CLOSE = 0x0010
WM_HOTKEY = 0x0312

ERROR_ALREADY_EXISTS = 183

MB_OK = 0x00000000
MB_ICONERROR = 0x00000010
MB_ICONWARNING = 0x00000030
MB_ICONINFORMATION = 0x00000040
MB_SETFOREGROUND = 0x00010000

user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
user32.RegisterHotKey.restype = wintypes.BOOL
user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
user32.UnregisterHotKey.restype = wintypes.BOOL
user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL
user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostThreadMessageW.restype = wintypes.BOOL
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostMessageW.restype = wintypes.BOOL
user32.MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
user32.MessageBoxW.restype = ctypes.c_int
user32.MessageBeep.argtypes = [wintypes.UINT]
user32.MessageBeep.restype = wintypes.BOOL
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = ctypes.c_short

kernel32.GetCurrentThreadId.restype = wintypes.DWORD
kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.CreateMutexW.restype = wintypes.HANDLE


def message_box(title: str, text: str, icon: int = MB_ICONINFORMATION) -> None:
    '''Show a blocking message box (works without Tk, e.g. under pythonw).'''
    user32.MessageBoxW(None, text, title, MB_OK | icon | MB_SETFOREGROUND)


def beep(kind: int = MB_OK) -> None:
    user32.MessageBeep(kind)


def acquire_single_instance_mutex(name: str) -> bool:
    '''
    Return True if this is the only process holding the named mutex.
    The handle is intentionally leaked: Windows releases it when the process exits.
    '''
    handle = kernel32.CreateMutexW(None, False, name)
    if not handle:
        return False
    return ctypes.get_last_error() != ERROR_ALREADY_EXISTS
