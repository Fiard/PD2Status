using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;

#pragma warning disable CS1591

namespace WindowsInput
{
    public static class InterceptKeys
    {
        public interface IKeyEventProc
        {
            void keyDown(int vkCode);
            void keyUp(int vkCode);
        }
        
        private const int WH_KEYBOARD_LL = 13;
        private const int WM_KEYDOWN = 0x0100;
        private const int WM_KEYUP = 0x0101;
        private const int WM_SYSKEYUP = 0x0105;
        private static readonly LowLevelKeyboardProc _proc = HookCallback;
        private static readonly int HookId;
        private static readonly object _lock = new object();
        private static readonly List<IKeyEventProc> _listeners = new List<IKeyEventProc>();
        
        static InterceptKeys()
        {
            HookId = SetHook(_proc);
            AppDomain.CurrentDomain.ProcessExit += (s, a) => {
                UnhookWindowsHookEx(HookId);
            };
        }

        public static void addListener(IKeyEventProc listener)
        {
            lock (_lock) {
                if (!_listeners.Contains(listener)) _listeners.Add(listener);
            }
        }

        public static void removeListener(IKeyEventProc listener)
        {
            lock (_lock) {
                _listeners.Remove(listener);
            }
        }

        private static int SetHook(LowLevelKeyboardProc proc)
        {
            using (var curProcess = Process.GetCurrentProcess())
            using (var curModule = curProcess.MainModule) {
                return SetWindowsHookEx(WH_KEYBOARD_LL, proc, GetModuleHandle(curModule.ModuleName), 0);
            }
        }

        private delegate int LowLevelKeyboardProc(int nCode, int wParam, int lParam);

        [ThreadStatic] private static IKeyEventProc[] _iterateListeners;

        private static int HookCallback(int nCode, int wParam, int lParam)
        {
            // ReSharper disable once InconsistentlySynchronizedField
            if (_listeners.Count == 0) return CallNextHookEx(HookId, nCode, wParam, lParam);
            if (nCode < 0) return CallNextHookEx(HookId, nCode, wParam, lParam);
            if (wParam != WM_KEYDOWN && wParam != WM_KEYUP && wParam != WM_SYSKEYUP) return CallNextHookEx(HookId, nCode, wParam, lParam);

            var vkCode = Marshal.ReadInt32((IntPtr) lParam);

            int count;
            lock (_lock) {
                count = _listeners.Count;
                if (_iterateListeners == null || _iterateListeners.Length < count) {
                    _iterateListeners = new IKeyEventProc[count];
                }
                _listeners.CopyTo(_iterateListeners);
            }

            for (var i = 0; i < count; i++) {
                var listener = _iterateListeners[i];
                switch (wParam) {
                    case WM_KEYDOWN:
                        listener.keyDown(vkCode);
                        break;
                    case WM_KEYUP:
                    case WM_SYSKEYUP:
                        listener.keyUp(vkCode);
                        break;
                    default:
                        throw new ArgumentException();
                }
            }

            return CallNextHookEx(HookId, nCode, wParam, lParam);
        }

        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern int SetWindowsHookEx(int idHook, LowLevelKeyboardProc lpfn, int hMod, uint dwThreadId);

        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool UnhookWindowsHookEx(int hhk);

        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern int CallNextHookEx(int hhk, int nCode, int wParam, int lParam);

        [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern int GetModuleHandle(string lpModuleName);
    }
}
